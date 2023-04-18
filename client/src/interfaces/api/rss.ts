import { ApiResponse } from './apiResponse';

export interface FeedsPayload {
    feeds: string[];
}

export type FeedsApiResponse = ApiResponse<FeedsPayload>;
