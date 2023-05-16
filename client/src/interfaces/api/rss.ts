import { ApiResponse } from './apiResponse';

export interface RssFeed {
    source: string;
    name: string;
    feed: string;
}

export interface FeedsPayload {
    feeds: RssFeed[];
}

export type FeedsApiResponse = ApiResponse<FeedsPayload>;
