use crate::{
    error::RssError,
    prelude::*,
    prisma::{self, PrismaClient},
};
use feed_rs::model::Feed;
use nom::{
    IResult,
    sequence::delimited,
    // see the "streaming/complete" paragraph lower for an explanation of these submodules
    character::complete::char,
    bytes::complete::is_not,
    bytes::complete::take_until
};

use regex::Regex;
use crate::prisma::users::SetParam;


pub async fn scrape_rss_feeds(client: &PrismaClient) -> Result<()> {
    let rss_feeds = client.rss_entries().find_many(vec![]).exec().await?;

    for rss_feed in rss_feeds {
        let source_id = rss_feed.source_id;
        let rss_feed = rss_feed.feed;

        let mut label_batch = Vec::new();
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

            let description = entry
                .summary
                .as_ref()
                .map(|description| description.content.to_string());



            // Create a regex pattern to match HTML tags
            let mut string_html: Option<String>=None;
            if description.is_some(){
                let pattern = Regex::new(r"<.*?>").unwrap();
                let clean_de = description.as_ref().map(|description| description.to_string()).unwrap();
                let clean_html = pattern.replace_all(&clean_de, "");
                string_html = clean_html.into_owned().into();
            }

            let photo = get_photos_from_entry(&entry).into_iter().next();

            let pub_date: Option<chrono::DateTime<chrono::FixedOffset>> =
                entry.published.map(|date| date.into());

            let labels: Vec<String> = entry
                .categories
                .iter()
                .map(|category| category.term.clone())
                .collect();


            log::debug!("title: `{title}`, url: `{url}`, photo: `{photo:?}`, description: {string_html:?}, pub_date: `{pub_date:?}`, tags: {labels:?}");

            /* insert scraped data into db */

            // TODO: Make labels work :)
            // TODO: Connect labels to articles.

            // insert labels
            for label in labels {
                label_batch.push(client.labels().upsert(
                    prisma::labels::name::equals(label.clone()),
                    prisma::labels::create(label, vec![]),
                    vec![],
                ))
            }
            
            let mut description_article= prisma::news_articles::description::set(description);


            // insert articles
            if string_html.is_some()
            {
                description_article = prisma::news_articles::description::set(string_html);
            }

            article_batch.push(client.news_articles().upsert(
                    prisma::news_articles::url::equals(url.clone()),
                    prisma::news_articles::create(
                        prisma::news_sources::id::equals(source_id),
                        url,
                        title,
                        vec![
                            prisma::news_articles::photo::set(photo),
                            prisma::news_articles::publication_date::set(pub_date),
                            description_article
                        ],
                    ),
                    // Update is not needed, because we want to ignore articles that have been inserted
                    // before.
                    vec![],
                ));
        }

        client._batch((label_batch, article_batch)).await?;
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
            .filter_map(|content| {
                content
                    .url
                    .as_ref()
                    .map_or(None, |url| Some(url.to_string()))
            })
            .collect();

        photos.extend(rss2_photos);
    }

    photos
}
