#![allow(unused)]

use crate::{prelude::*, prisma::PrismaClient};
use rss::Channel;
use std::{
    fs,
    io::{BufRead, BufWriter, Write},
};

mod error;
mod prelude;
mod prisma;

#[tokio::main]
async fn main() {
    // let client = prisma::new_client()
    //     .await
    //     .expect("failed to connect to prisma database");
    // println!("Start scraping the feeds ...");
    // parse_rss_feeds(&client).await.unwrap();
    // println!("Finished scraping!")

    check_rss_feeds_from_file("rss-feeds.txt", "tmp.txt")
        .await
        .unwrap();
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

        let channel = match Channel::read_from(&content[..]) {
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

async fn parse_rss_feeds(client: &PrismaClient) -> Result<()> {
    let mut file = fs::File::create("rss-feeds.txt").expect("failed to open file");
    let mut buf = BufWriter::new(&mut file);

    let rss_feeds = &client.rss_entries().find_many(vec![]).exec().await.unwrap();
    println!("amount of rss feeds: {}", rss_feeds.len());

    let mut success = 0;

    for feed in rss_feeds {
        let url = &feed.feed;
        let content = reqwest::get(url).await?.bytes().await?;

        // println!("{}", std::str::from_utf8(&content[..]).unwrap());

        let channel = match Channel::read_from(&content[..]) {
            Ok(channel) => channel,
            Err(err) => continue,
        };

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
