import { ApiResponse } from './apiResponse';

export interface LabelsPayload {
    labels: string[];
}

export type LabelsApiResponse = ApiResponse<LabelsPayload>;
