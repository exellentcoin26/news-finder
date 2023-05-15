import { ApiResponse } from './apiResponse';

export interface ArticleEntry {
    title: string;
    description?: string;
    photo?: string;
    link: string;
    publication_date : number
}

export interface ArticleSourceEntry {
    article: ArticleEntry;
    source: string;
}

export interface ArticlePayload {
    articles: ArticleSourceEntry[];
}

export interface SimilarArticleEntry {
    source: string;
    link: string;
}

export interface SimilarArticlePayload {
    articles: SimilarArticleEntry[];
}

export type ArticleApiResponse = ApiResponse<ArticlePayload>;

export type SimilarArticleApiResponse = ApiResponse<SimilarArticlePayload>