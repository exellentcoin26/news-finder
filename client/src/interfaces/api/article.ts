export interface ArticleEntry {
    title: string;
    description?: string;
    photo?: string;
}

export interface ArticleSourceEntry {
    article: ArticleEntry;
    source: string;
}

export interface ArticleApiResponse {
    articles: ArticleSourceEntry[];
}
