#![allow(unused)]

use crate::{error::PrismaError, prelude::*, prisma::PrismaClient};
use dotenv::dotenv;
use error::RssError;
use feed_rs::model::Feed;
use std::{
    fs,
    io::{BufRead, BufWriter, Write},
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

    // check_rss_feeds_from_file("rss-feeds.txt", "tmp.txt")
    //     .await
    //     .unwrap();
}

async fn scrape_rss_feeds(client: &PrismaClient) -> Result<()> {
    let rss_feeds = match client.rss_entries().find_many(vec![]).exec().await {
        Ok(rss_feeds) => rss_feeds,
        Err(err) => return Err(PrismaError::from(err).into()),
    };

    for rss_feed in rss_feeds {
        let rss_feed = rss_feed.feed;

        let feed = match get_rss_and_validate(&rss_feed).await {
            Ok(feed) => feed,
            Err(err) => {
                // An error occurred where either `reqwest` failed to fetch the url or the rss feed
                // is invalid.
                // TODO: Print an error here about the feed.
                // TODO: Should I remove the feed if it was invalid? It is possible that the feed
                // was reachable at this time, but is completely valid.
                eprintln!("Rss feed invalid or (temporarily) not reachable");
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
                Some(title) => title.content,
                None => {
                    eprintln!("Article entry has no title (rss feed: `{rss_feed}`)");
                    continue;
                }
            };

            let description = entry
                .summary
                .map(|description| description.content.to_string());

            let photo = entry
                .links
                .iter()
                .filter(|link| {
                    link.media_type
                        .as_ref()
                        .map_or(false, |media_type| media_type == "image/jpeg")
                })
                .next()
                .map(|link| link.href.to_string());

            let pub_date = entry.published;

            println!("title: `{title}`, url: `{url}`, photo: `{photo:?}`, description: {description:?}, pub_date: `{pub_date:?}`");
        }
    }

    Ok(())
}

async fn check_rss_feeds_from_file(input_file_name: &str, output_file_name: &str) -> Result<()> {
    let input_file = fs::File::open(input_file_name)?;
    let mut output_file = fs::File::create(output_file_name)?;

    let input = std::io::BufReader::new(input_file);
    let mut output = std::io::BufWriter::new(&mut output_file);

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

        let feed = match feed_rs::parser::parse(&content[..]) {
            Ok(channel) => channel,
            Err(err) => {
                rss_errors.push((
                    rss_feed,
                    err.into(),
                    std::str::from_utf8(&content[..]).unwrap().to_string(),
                ));
                continue;
            }
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
