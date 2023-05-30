use std::path::PathBuf;

use clap::{Args, Parser, Subcommand};

#[derive(Parser)]
#[command(author, version, about, long_about = None)]
pub struct Cli {
    #[command(subcommand)]
    pub command: CliCommands,
}

#[derive(Subcommand)]
pub enum CliCommands {
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
        args: CliScrapeArgs,
    },
}

#[derive(Args)]
#[group(multiple = false)]
pub struct CliScrapeArgs {
    /// Run once
    #[arg(long)]
    pub once: bool,
}
