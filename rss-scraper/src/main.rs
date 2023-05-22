use crate::{
    counter::RssCounter,
    prelude::*,
    prisma::{rss_entries::Data as PrismaFeed, PrismaClient},
    scraper::{scrape_rss_feed, scrape_rss_feeds},
};
use chrono::Duration;
use clap::{error::ErrorKind, Args, CommandFactory, Parser, Subcommand};
use dotenv::dotenv;
use std::{
    collections::BTreeSet,
    fs,
    io::{BufRead, BufReader, BufWriter, Write},
    path::PathBuf,
    time::Instant,
};

mod counter;
mod error;
mod prelude;
mod prisma;
mod scraper;

#[derive(Parser)]
#[command(author, version, about, long_about = None)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Check RSS feeds validity from input file
    Check {
        /// File to read feeds from
        #[arg(short, long, value_name = "INPUT_FILE", default_value = "input.txt")]
        input: PathBuf,

        /// File to write successful feeds to
        #[arg(short, long, value_name = "OUTPUT_FILE", default_value = "working.txt")]
        output: PathBuf,
    },
    /// Run the rss-scraper
    Run {
        #[command(flatten)]
        args: ScrapeArgs,
    },
}

#[derive(Args)]
#[group(multiple = false)]
struct ScrapeArgs {
    /// Run once
    #[arg(long)]
    once: bool,
}

#[tokio::main]
async fn main() -> Result<()> {
    let cli = Cli::parse();

    // load environment variables from `.env` file if present
    dotenv().ok();

    env_logger::builder()
        .format_timestamp(None)
        .format_indent(Some(4))
        .init();

    match cli.command {
        Commands::Check { input, output } => {
            if !input.exists() {
                let mut cmd = Cli::command();
                cmd.error(ErrorKind::Io, "Input file does not exist").exit();
            }

            check_rss_feeds_from_file(&input, &output).await?;
        }
        Commands::Run { args } => {
            if args.once {
                let client = prisma::new_client()
                    .await
                    .expect("failed to create prisma client");
                run_scraper(None, &client).await?;
            } else {
                start_scrape_job().await?;
            }
        }
    }

    Ok(())
}

async fn start_scrape_job() -> Result<()> {
    let client = prisma::new_client()
        .await
        .expect("failed to create prisma client");

    let mut counters = BTreeSet::new();

    let force_update_counters = true;

    // interval in nanoseconds
    let interval = 4e9_f64;

    let mut delta = 0_f64;
    let mut last_time = Instant::now();

    loop {
        let now = Instant::now();
        delta += (now - last_time).as_nanos() as f64 / interval;
        last_time = now;

        if delta >= 1.0 {
            delta -= 1.0;

            use prisma::flags::UniqueWhereParam::NameEquals;

            let should_update_counters = client
                .flags()
                .find_unique(NameEquals("rss_feeds_modified".to_string()))
                .exec()
                .await?;

            let should_update_counters = match should_update_counters {
                Some(tuple) => tuple.value,
                None => {
                    client
                        .flags()
                        .create("rss_feeds_modified".to_string(), false, vec![])
                        .exec()
                        .await?;
                    false
                }
            };

            if should_update_counters || force_update_counters {
                // query the interval of all rss feeds
                for feed in client.rss_entries().find_many(vec![]).exec().await? {
                    counters.insert(RssCounter {
                        feed,
                        start_time: Instant::now(),
                    });
                }
            }

            let mut next_run: Option<Duration> = None;
            let mut new_counters = Vec::new();
            for feed_counter in counters.iter() {
                let interval =
                    Duration::from_std(Instant::now() - feed_counter.start_time).unwrap();

                if interval.num_seconds() >= feed_counter.feed.interval as i64 * 60 {
                    run_scraper(Some(&feed_counter.feed), &client).await?;
                    new_counters.push(RssCounter {
                        feed: feed_counter.feed.clone(),
                        start_time: Instant::now(),
                    });
                } else {
                    let time_till_next_run =
                        Duration::seconds(feed_counter.feed.interval as i64 * 60) - interval;
                    next_run = match next_run {
                        Some(next_run) => Some(next_run.min(time_till_next_run)),
                        None => Some(time_till_next_run),
                    }
                }
            }

            for new_counter in new_counters {
                counters.replace(new_counter);
            }

            if let Some(next_run) = next_run {
                log::info!("Next run in {} seconds", next_run.num_seconds());
            } else {
                log::info!("No feeds to scrape.")
            }
        }
    }
}

async fn run_scraper(feed: Option<&PrismaFeed>, client: &PrismaClient) -> Result<()> {
    match feed {
        Some(feed) => {
            log::info!("Start scraping rss feed {} ...", feed.feed);
            scrape_rss_feed(feed, client).await?;
        }
        None => {
            log::info!("Start scraper rss feeds ...");
            scrape_rss_feeds(client).await?;
        }
    }
    client
        .flags()
        .upsert(
            prisma::flags::name::equals("articles_modified".to_string()),
            prisma::flags::create("articles_modified".to_string(), true, vec![]),
            vec![prisma::flags::value::set(true)],
        )
        .exec()
        .await?;

    log::info!("Successfully scraped feeds!");

    Ok(())
}

#[allow(dead_code)]
async fn check_rss_feeds_from_file(
    input_file_name: &PathBuf,
    output_file_name: &PathBuf,
) -> Result<()> {
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

        let _ = output.write(rss_feed.as_bytes())?;
        let _ = output.write(b"\n")?;
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
