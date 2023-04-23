use crate::{error::RssError,
            prelude::*,
            prisma::{self, PrismaClient}, scraper};
use feed_rs::model::Feed;



use crate::prisma::{news_article_labels, news_articles};


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
            // removing <p> tags using regex library
            let description = entry
                .summary
                .as_ref()
                .map(|description| description.content.to_string());

            let photo = get_photos_from_entry(&entry).into_iter().next();

            let pub_date: Option<chrono::DateTime<chrono::FixedOffset>> =
                entry.published.map(|date| date.into());

            let labels: Vec<String> = entry
                .categories
                .iter()
                .map(|category| category.term.clone())
                .collect();

            let mut new_labels: Vec<String>=Vec::new();
            for label in labels
            {
                let outerparts: Vec<&str> = label.split(':').collect(); // Split the string by ':' and collect the parts into a outerparts
                if outerparts.len() != 1{
                    if outerparts[0] == "structure"
                        {
                            let innerparts: Vec<&str> = outerparts[1].split("/").collect();
                            if innerparts.len() > 1
                            {
                                new_labels.push(innerparts[1].to_string());
                            }else {
                                new_labels.push(innerparts[0].to_string());
                            }
                        }

                }else
                {
                    new_labels.push(outerparts[0].to_string());
                }
            }




            //log::debug!("title: `{title}`, url: `{url}`, photo: `{photo:?}`, description: {description:?}, pub_date: `{pub_date:?}`, tags: {labels:?}");
            // log::debug!("tags: {labels:?}");
            /* insert scraped data into db */

            // TODO: Make labels work :)
            // TODO: Connect labels to articles.

            // insert labels

            let labels= client.labels().create(new_labels[0].clone(),
                                   vec![]
            );

            let temp_news_article_labels = client.news_article_labels().create(
                    news_articles::create(
                        news_articles::source_id::set(source_id),
                        news_articles::url::set(url),
                        news_articles::title::set(title),
                        vec![
                            news_articles::description::set(description),
                            news_articles::photo::set(photo),
                            news_articles::publication_date::set(pub_date)
                        ]),
                prisma::labels::SetParam(labels),
                    vec![]
            );















        }
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
