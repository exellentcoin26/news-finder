use feed_rs::model::Feed;
use prisma_client_rust::query_core::schema_builder::capitalize;

use regex::Regex;

use crate::prisma::{news_article_labels, news_articles};
use crate::{
    error::RssError,
    prelude::*,
    prisma::{self, PrismaClient},
    scraper,
};
use feed_rs::model::Feed;
use regex::Regex;

pub async fn scrape_rss_feeds(client: &PrismaClient) -> Result<()> {
    let rss_feeds = client.rss_entries().find_many(vec![]).exec().await?;

    for rss_feed in rss_feeds {
        let source_id = rss_feed.source_id;
        let rss_feed = rss_feed.feed;

        let mut labels_with_articles = Vec::new();
        let mut article_batch = Vec::new();

        let feed = match get_rss_and_validate(&rss_feed).await {
            Ok(feed) => feed,
            Err(_) => {
                // An error occurred where either `reqwest` failed to fetch the url or the rss feed
                // is invalid.
                // TODO: Should I remove the feed if it was invalid? It is possible that the feed
                // was reachable at this time, but is completely valid.
                log::error!(
                    "Rss feed invalid or (temporarily) not reachable (rss feed: `{rss_feed}`)"
                );
                continue;
            }
        };

        // TODO: Store the language of the article for equality checking

        /* scrape the rss feed */
        for entry in feed.entries {
            /*
                Required fields:
                    * Source id
                    * Url
                    * Title

                Optional fields:
                    * Photo
                    * Description
                    * Publication date
                    * Labels
            */

            let url = match entry
                .links
                .iter()
                .filter(|link| {
                    if let Some(ref media_type) = link.media_type {
                        return media_type == "text/html";
                    }

                    true
                })
                .next()
            {
                Some(link) => link.href.to_string(),
                None => {
                    eprintln!("Article entry has no link to the article (rss feed: `{rss_feed}`)");
                    continue;
                }
            };

            let title = match entry.title {
                Some(ref title) => title.content.clone(),
                None => {
                    eprintln!("Article entry has no title (rss feed: `{rss_feed}`)");
                    continue;
                }
            };

            // removing <p> tags using regex library
            let description = entry
                .summary
                .as_ref()
                .map(|description| description.content.to_string())
            {
                Some(description) => {
                    let pattern =
                        Regex::new(r"<.*?>").expect("failed to build HTML bracket matching regex");
                    Some(pattern.replace_all(&description, "").into_owned())
                }
                None => None,
            };

            let photo = get_photos_from_entry(&entry).into_iter().next();

            let pub_date: Option<chrono::DateTime<chrono::FixedOffset>> =
                entry.published.map(|date| date.into());

            let raw_labels: Vec<String> = entry
                .categories
                .iter()
                .map(|category| category.term.clone())
                .collect();

            let mut labels = Vec::new();
            for label in raw_labels {
                if label.contains(":") {
                    if label.contains("structure") {
                        let pattern = Regex::new(r"structure:(?:.*/)?(?P<category>[^/]+)/?$")
                            .expect("failed to build regex");
                        let label = match pattern.captures(&label) {
                            Some(captures) => match captures.name("category") {
                                Some(matches) => matches.as_str().to_string(),
                                None => "".to_string(),
                            },
                            None => label.to_string(),
                        };
                        if !label.is_empty() {
                            labels.push(label);
                        }
                    } else {
                        Some(());
                    }
                } else {
                    labels.push(label);
                }
            }

            log::debug!("title: `{title}`, url: `{url}`, photo: `{photo:?}`, description: {description:?}, pub_date: `{pub_date:?}`, tags: {labels:?}");

            /* insert scraped data into db */

            // TODO: Make labels work :)
            // TODO: Connect labels to articles.

            // insert labels

            article_batch.push(client.news_articles().upsert(
                prisma::news_articles::url::equals(url.clone()),
                prisma::news_articles::create(
                    prisma::news_sources::id::equals(source_id),
                    url.clone(),
                    title,
                    vec![
                        prisma::news_articles::description::set(description),
                        prisma::news_articles::photo::set(photo),
                        prisma::news_articles::publication_date::set(pub_date),
                    ],
                ),
                // Update is not needed, because we want to ignore articles that have been inserted
                // before.
                vec![],
            ));

            for label in labels {
                labels_with_articles.push((label.clone(), url.clone()))
            }
        }

        client._batch(article_batch).await?;

        // insert labels
        let mut label_batch = Vec::new();

        for (label, article_url) in labels_with_articles {
            let article = client
                .news_articles()
                .find_unique(prisma::news_articles::url::equals(article_url.clone()))
                .exec()
                .await?
                .ok_or(())
                .expect("no article found with that url");

            label_batch.push(client.news_article_labels().upsert(
                prisma::news_article_labels::UniqueWhereParam::IdLabelEquals(
                    article.id,
                    label.clone(),
                ),
                prisma::news_article_labels::create(
                    prisma::news_articles::url::equals(article_url.clone()),
                    label.clone(),
                    vec![],
                ),
                vec![],
            ))
        }

        client._batch(label_batch).await?;
    }

    Ok(())
}

async fn get_rss_and_validate(url: &str) -> std::result::Result<Feed, RssError> {
    let content = reqwest::get(url).await?.bytes().await?;
    let feed = feed_rs::parser::parse(&content[..])?;

    Ok(feed)
}

/// Returns a vector of photo urls found in the entry.
/// Locations:
///     * Atom: entry::links with media_type equal to `image/jpeg`.
///     * Rss 2.0: entry::content::src with type equal to `image/jpeg`.
fn get_photos_from_entry(entry: &feed_rs::model::Entry) -> Vec<String> {
    let mut photos: Vec<String> = entry
        .links
        .iter()
        // Atom format
        .filter(|&link| {
            link.media_type.as_ref().map_or(false, |media_type| {
                media_type == "image/jpeg" || media_type == "image/png"
            })
        })
        .map(|link| link.href.clone())
        .collect();

    // Rss 2.0 format
    for media_entry in &entry.media {
        let rss2_photos: Vec<String> = media_entry
            .content
            .iter()
            .filter(|content| {
                content
                    .content_type
                    .as_ref()
                    .map_or(true, |content_type| content_type.type_() == mime::IMAGE)
            })
            .filter_map(|content| content.url.as_ref().map(|url| url.to_string()))
            .collect();

        photos.extend(rss2_photos);
    }

    photos
}
