import { Col, Container, Row, Dropdown } from 'react-bootstrap';
import { useEffect, useState } from 'react';

import {
    ArticleApiResponse,
    ArticleSourceEntry,
} from '../interfaces/api/article';
import {
    Article,
    ArticlePlaceholder,
    NoArticlesToShow,
} from '../components/Article';
import ErrorPlaceholder from '../components/Error';
import { LabelBar } from '../components/LabelBar';
import '../styles/Home.css';

const getArticlesFromServer = async (
    amount = 50,
    offset = 0,
    label = '',
    sortBy: 'Recency' | 'Popularity' | 'Source',
    errorHandler: () => void,
): Promise<ArticleSourceEntry[]> => {
    const serverUrl =
        import.meta.env['VITE_SERVER_URL'] || 'http://localhost:5000';

    const response = await (async (): Promise<Response> => {
        try {
            return await fetch(
                serverUrl +
                    '/article/?' +
                    new URLSearchParams({
                        amount: amount.toString(),
                        offset: offset.toString(),
                        label: label,
                        sortBy: sortBy.toLowerCase(),
                    }),
            );
        } catch (e) {
            console.error(e);
            errorHandler();
            throw e;
        }
    })();

    const body = await response.text();

    const articleApiResponse = ((): ArticleApiResponse => {
        try {
            return JSON.parse(body);
        } catch (e) {
            console.debug(body);
            throw e;
        }
    })();

    if (!response.ok) {
        errorHandler();
    }

    if (articleApiResponse.data == null) {
        // should always be caught with the error handler. This check is only needed for the type system.
        throw new Error('data property on `ArticleApiResponse` is not set');
    }

    return articleApiResponse.data.articles.map((articleSource) => {
        return articleSource;
    });
};

const Home = () => {
    const [articles, setArticles] = useState<ArticleSourceEntry[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [hasErrored, setHasErrored] = useState(false);
    const [sortBy, setSortBy] = useState<'Recency' | 'Popularity' | 'Source'>(
        'Recency',
    );

    const handleArticleErrors = () => {
        setHasErrored(true);
    };

    useEffect(() => {
        (async () => {
            try {
                const articles = await getArticlesFromServer(
                    50,
                    0,
                    '',
                    sortBy,
                    handleArticleErrors,
                );
                setArticles(articles);
            } catch (error) {
                console.error(error);
            } finally {
                setIsLoading(false);
            }
        })();
    }, [sortBy]);

    const handleLabelChange = async (label: string) => {
        setIsLoading(true);
        try {
            const articles = await getArticlesFromServer(
                50,
                0,
                label,
                sortBy,
                handleArticleErrors,
            );
            setArticles(articles);
        } catch (error) {
            console.error(error);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <Container className={'home-container'}>
            <Container>
                <LabelBar onClick={handleLabelChange} />
            </Container>
            <br />
            <Container style={{ display: 'flex', justifyContent: 'right' }}>
                <Dropdown>
                    <Dropdown.Toggle
                        style={{
                            backgroundColor: 'transparent',
                            color: 'black',
                            borderColor: 'transparent',
                        }}
                    >
                        {sortBy}
                    </Dropdown.Toggle>

                    <Dropdown.Menu>
                        <Dropdown.Item onClick={() => setSortBy('Recency')}>
                            Recency
                        </Dropdown.Item>
                        <Dropdown.Item onClick={() => setSortBy('Popularity')}>
                            Popularity
                        </Dropdown.Item>
                        <Dropdown.Item onClick={() => setSortBy('Source')}>
                            Source
                        </Dropdown.Item>
                    </Dropdown.Menu>
                </Dropdown>
            </Container>
            <br />
            {hasErrored ? (
                <ErrorPlaceholder />
            ) : isLoading ? (
                <ArticlePlaceholder />
            ) : articles.length == 0 ? (
                <NoArticlesToShow />
            ) : (
                <>
                    {articles.map((articleSource, index) => {
                        return (
                            <Row
                                // TODO: Use something better than index as key
                                key={index}
                                className={'home-article'}
                            >
                                <Col>
                                    <Article
                                        title={articleSource.article.title}
                                        {...(articleSource.article
                                            .description != null
                                            ? {
                                                  description:
                                                      articleSource.article
                                                          .description,
                                              }
                                            : {})}
                                        {...(articleSource.article.photo != null
                                            ? {
                                                  img_src:
                                                      articleSource.article
                                                          .photo,
                                              }
                                            : {})}
                                        article_link={
                                            articleSource.article.link
                                        }
                                        source={articleSource.source}
                                        {...(articleSource.article
                                            .publication_date != null
                                            ? {
                                                  timestamp:
                                                      articleSource.article
                                                          .publication_date,
                                              }
                                            : {})}
                                    />
                                </Col>
                            </Row>
                        );
                    })}
                </>
            )}
        </Container>
    );
};

export default Home;
