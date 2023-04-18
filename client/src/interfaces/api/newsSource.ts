import { ApiResponse } from './apiResponse';

export interface SourcesPayload {
    sources: string[];
}

export type SourcesApiResponse = ApiResponse<SourcesPayload>;
