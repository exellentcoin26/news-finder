import { ApiResponse } from './apiResponse';

export interface ArticleEntry {
    title: string;
    description?: string;
    photo?: string;
    link: string;
}

export interface ArticleSourceEntry {
    article: ArticleEntry;
    source: string;
}

export interface ArticlePayload {
    articles: ArticleSourceEntry[]
}


export type ArticleApiResponse = ApiResponse<ArticlePayload>;
