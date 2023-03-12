#![allow(unused)]

use crate::{prelude::*, prisma::PrismaClient};
use rss::{validation::Validate, Channel};
use std::{
    fs,
    io::{BufWriter, Write},
};

mod error;
mod prelude;
mod prisma;

#[tokio::main]
async fn main() {
    let client = prisma::new_client()
        .await
        .expect("failed to connect to prisma database");
    println!("Start scraping the feeds ...");
    parse_rss_feeds(&client).await.unwrap();
    println!("Finished scraping!")
}

async fn parse_rss_feeds(client: &PrismaClient) -> Result<()> {
    let mut file = fs::File::create("rss-feeds.txt").expect("failed to open file");
    let mut buf = BufWriter::new(&mut file);

    let rss_feeds = &client.rss_entries().find_many(vec![]).exec().await.unwrap();
    println!("amount of rss feeds: {}", rss_feeds.len());

    let mut rss_errors = Vec::new();

    let mut success = 0;

    for feed in rss_feeds {
        let url = &feed.feed;
        let content = reqwest::get(url).await?.bytes().await?;

        // println!("{}", std::str::from_utf8(&content[..]).unwrap());

        let channel = match Channel::read_from(&content[..]) {
            Ok(channel) => channel,
            Err(err) => continue,
        };

        if let Err(err) = channel.validate() {
            rss_errors.push((url, err));
        }

        println!("Successful rss feed: `{url}`");

        success += 1;

        buf.write(url.as_bytes());
        buf.write(b"\n");

        // for item in channel.items() {
        //     println!("{item:?}");
        // }
    }

    buf.flush().unwrap();
    println!("Amount of successful rss feeds: {success}");

    Ok(())
}
