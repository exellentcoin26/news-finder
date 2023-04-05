use crate::{prelude::*, scraper::scrape_rss_feeds};
use clap::{error::ErrorKind, Args, CommandFactory, Parser, Subcommand};
use dotenv::dotenv;
use job_scheduler_ng::{Job, JobScheduler};
use std::{
    fs,
    io::{BufRead, BufReader, BufWriter, Write},
    path::PathBuf,
    time::Duration,
};

mod error;
mod prelude;
mod prisma;
mod scraper;

#[derive(Parser)]
#[command(author, version, about, long_about=None)]
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

    /// Run on the given interval in minutes
    #[arg(short, long, value_name = "INTERVAL", default_value_t = 10)]
    interval: u32,
}

#[tokio::main]
async fn main() -> Result<()> {
    let cli = Cli::parse();

    // load environment variables from `.env` file if present
    dotenv().ok();

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
                run_scraper().await;
            } else {
                start_scrape_job(args.interval);
            }
        }
    }

    Ok(())
}

fn start_scrape_job(interval: u32) -> ! {
    let mut schedule = JobScheduler::new();

    let mut job = Job::new(
        // run every 10 minutes
        format!("* 1/{} * * * * *", interval)
            .parse()
            .expect("failed to parse cron job time schedule"),
        || {
            tokio::spawn(run_scraper());
        },
    );

    job.limit_missed_runs(0);

    schedule.add(job);

    loop {
        schedule.tick();
        std::thread::sleep(Duration::from_secs(3));
        println!(
            "Time remaining untill next job starts: {} seconds.",
            schedule.time_till_next_job().as_secs()
        )
    }
}

async fn run_scraper() {
    let client = prisma::new_client()
        .await
        .expect("failed to connect to prisma database");

    println!("Start scraping the rss feeds ...");

    scrape_rss_feeds(&client).await.unwrap();

    println!("Successfully scraped rss feeds!");
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
