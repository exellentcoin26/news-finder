use crate::prisma::rss_entries::Data as Feed;
use std::time::Instant;

pub struct RssCounter {
    /// Prisma data of the rss feed.
    pub feed: Feed,
    /// Start time of the counter.
    pub start_time: Instant,
}
