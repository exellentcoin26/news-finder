import { Col, Container, Row } from 'react-bootstrap';
import { useEffect, useState } from 'react';

import { ArticleApiResponse, ArticleEntry } from '../interfaces/api/Article';
import { Article, ArticlePlaceholder } from '../components/Article';

import '../styles/Home.css';

const getArticlesFromServer = async (_amount = 0): Promise<ArticleEntry[]> => {
    const serverUrl =
        import.meta.env['VITE_SERVER_URL'] || 'http://localhost:5000';
    const response = await fetch(serverUrl + '/article');
    const body = await response.text();

    const articles = ((): ArticleApiResponse => {
        try {
            return JSON.parse(body);
        } catch (e) {
            console.debug(body);
            throw e;
        }
    })();

    return articles.articles.map((articleSource) => {
        return articleSource.article;
    });
};

const Home = () => {
    const [articles, setArticles] = useState<ArticleEntry[]>([]);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const fetchArticles = async () => {
            try {
                const articles = await getArticlesFromServer();
                setArticles(articles);
            } catch (error) {
                console.error(error);
            } finally {
                setIsLoading(false);
            }
        };

        fetchArticles();
    }, []);

    return (
        <Container className={'home-container'}>
            {isLoading ? (
                <ArticlePlaceholder />
            ) : (
                articles.map(({ title, description, photo, link }, index) => {
                    return (
                        <Row
                            // TODO: Use something better than index as key
                            key={index}
                            className={'home-article'}
                        >
                            <Col>
                                <Article
                                    title={title}
                                    {...(description != null
                                        ? { description: description }
                                        : {})}
                                    {...(photo != null
                                        ? { img_src: photo }
                                        : {})}
                                    article_link={link}
                                />
                            </Col>
                        </Row>
                    );
                })
            )}
        </Container>
    );
};

export default Home;
