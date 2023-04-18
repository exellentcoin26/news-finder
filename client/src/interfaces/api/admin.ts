import { ApiResponse } from './apiResponse';

export interface AdminStatusPayload {
    admin: boolean;
}

export type AdminStatusApiResponse = ApiResponse<AdminStatusPayload>;
