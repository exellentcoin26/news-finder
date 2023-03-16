use crate::{prelude::*, prisma::PrismaClient};
use dotenv::dotenv;
use error::RssError;
use feed_rs::model::Feed;
use std::{
    fs,
    io::{BufRead, BufReader, BufWriter, Write},
};

mod error;
mod prelude;
mod prisma;

#[tokio::main]
async fn main() {
    // load environment variables from `.env` file if present
    dotenv().ok();

    let client = prisma::new_client()
        .await
        .expect("failed to connect to prisma database");
    println!("Start scraping the rss feeds ...");
    scrape_rss_feeds(&client).await.unwrap();

    // check_rss_feeds_from_file("rss-feeds.txt", "working.txt")
    //     .await
    //     .unwrap();
}

async fn scrape_rss_feeds(client: &PrismaClient) -> Result<()> {
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
                eprintln!(
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

            let photo = get_photos_from_entry(&entry).into_iter().next();

            let pub_date: Option<chrono::DateTime<chrono::FixedOffset>> =
                entry.published.map(|date| date.into());

            let labels: Vec<String> = entry
                .categories
                .iter()
                .map(|category| category.term.clone())
                .collect();

            println!("title: `{title}`, url: `{url}`, photo: `{photo:?}`, description: {description:?}, pub_date: `{pub_date:?}`, tags: {labels:?}");

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

            // insert articles
            article_batch.push(client.news_articles().upsert(
                prisma::news_articles::url::equals(url.clone()),
                prisma::news_articles::create(
                    prisma::news_sources::id::equals(source_id),
                    url,
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
        }

        client._batch((label_batch, article_batch)).await?;
    }

    Ok(())
}

#[allow(dead_code)]
async fn check_rss_feeds_from_file(input_file_name: &str, output_file_name: &str) -> Result<()> {
    let input_file = fs::File::open(input_file_name)?;
    let mut output_file = fs::File::create(output_file_name)?;

    let input = BufReader::new(input_file);
    let mut output = BufWriter::new(&mut output_file);

    let mut rss_amount = 0;
    let mut success_amount = 0;
    let mut warn_amount = 0;

    let mut rss_errors: Vec<(String, Error, String)> = Vec::new();

    for line_result in input.lines() {
        let rss_feed = match line_result {
            Ok(rss_feed) => rss_feed,
            Err(err) => return Err(err.into()),
        };

        rss_amount += 1;

        let content = match reqwest::get(&rss_feed).await {
            Ok(content) => content.bytes().await?,
            Err(_) => {
                warn_amount += 1;
                println!("[=] Failed to retrieve rss feed: `{rss_feed}`");
                continue;
            }
        };

        if let Err(err) = feed_rs::parser::parse(&content[..]) {
            rss_errors.push((
                rss_feed,
                err.into(),
                std::str::from_utf8(&content[..]).unwrap().to_string(),
            ));
            continue;
        };

        success_amount += 1;

        println!("[+] Successful rss feed: `{}`", &rss_feed);

        output.write(rss_feed.as_bytes())?;
        output.write(b"\n")?;
    }

    for rss_error in &rss_errors {
        println!(
            "[-] Rss failed with error (rss: `{}`, error: `{:?}`, content: `{}`)",
            rss_error.0, rss_error.1, rss_error.2
        );
    }

    println!();
    println!("==========================================");
    println!("Successful: {success_amount}");
    println!("Failed: {}", rss_errors.len());
    println!("Not retrieveable: {warn_amount}");
    println!("Total: {rss_amount}");
    println!("==========================================");

    output.flush()?;

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
