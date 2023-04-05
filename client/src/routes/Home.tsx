import { Col, Row, Container } from 'react-bootstrap';
import { useEffect, useState } from 'react';

import { ArticleApiResponse, ArticleEntry } from '../interfaces/api/article';
import { Article, ArticlePlaceholder } from '../components/Article';

import '../styles/Home.css';

const getArticlesFromServer = async (_amount = 0): Promise<ArticleEntry[]> => {
    const serverUrl =
        import.meta.env['VITE_SERVER_URL'] || 'http://localhost:5000';
    const response = await fetch(serverUrl + '/article');

    // TODO: Make this more type safe. Here it is assumed to be correct and parsed as such.
    const articles: ArticleApiResponse = await response.json();

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
                // console.log(articles);
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
        <Container className="home-container">
            {isLoading ? (
                <ArticlePlaceholder />
            ) : (
                articles.map(({ title, description, photo }, index) => {
                    return (
                        <Row
                            // TODO: Use something better than index as key
                            key={index}
                            className={'home-article'}
                        >
                            <Col>
                                <Article
                                    title={title}
                                    {...(description !== undefined
                                        ? { description: description }
                                        : {})}
                                    {...(photo !== undefined
                                        ? { img_src: photo }
                                        : {})}
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
