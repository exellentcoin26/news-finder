use crate::prisma::rss_entries::Data as Feed;
use std::time::Instant;

pub struct RssCounter {
    /// Prisma data of the rss feed.
    pub feed: Feed,
    /// Start time of the counter.
    pub start_time: Instant,
}

impl Eq for RssCounter {}

impl PartialEq for RssCounter {
    fn eq(&self, other: &Self) -> bool {
        self.feed.id == other.feed.id
    }
}

impl PartialOrd for RssCounter {
    fn partial_cmp(&self, other: &Self) -> Option<std::cmp::Ordering> {
        self.feed.id.partial_cmp(&other.feed.id)
    }
}

impl Ord for RssCounter {
    fn cmp(&self, other: &Self) -> std::cmp::Ordering {
        self.feed.id.cmp(&other.feed.id)
    }
}
