//! Main crate error type.

#[derive(thiserror::Error, Debug)]
pub enum Error {
    #[error("Generic {0}")]
    Generic(String),

    #[error(transparent)]
    Reqwest(#[from] reqwest::Error),

    #[error(transparent)]
    Rss(#[from] feed_rs::parser::ParseFeedError),

    #[error(transparent)]
    Io(#[from] std::io::Error),
}
