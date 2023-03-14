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
    Prisma(#[from] PrismaError),

    #[error(transparent)]
    Io(#[from] std::io::Error),
}

#[derive(thiserror::Error, Debug)]
pub enum PrismaError {
    #[error(transparent)]
    Query(#[from] prisma_client_rust::QueryError),
}

#[derive(thiserror::Error, Debug)]
pub enum RssError {
    #[error(transparent)]
    ParseFeed(#[from] feed_rs::parser::ParseFeedError),

    #[error(transparent)]
    Reqwest(#[from] reqwest::Error),
}
