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
                console.log(articles);
                setArticles(articles);
            } catch (error) {
                console.log(error);
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
            {/*<Row className="home-article">*/}
            {/*    <Col>*/}
            {/*        <Article*/}
            {/*            title="Local Cat Elected Mayor of Small Town"*/}
            {/*            img_src="/images/cat.jpg"*/}
            {/*            description="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."*/}
            {/*        />*/}
            {/*    </Col>*/}
            {/*</Row>*/}
            {/*<Row className="home-article">*/}
            {/*    <Col>*/}
            {/*        <Article*/}
            {/*            title="Local Cat Elected Mayor of Small Town"*/}
            {/*            img_src="/images/cat.jpg"*/}
            {/*            description="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Sem fringilla ut morbi tincidunt. Faucibus interdum posuere lorem ipsum dolor. Pellentesque dignissim enim sit amet venenatis urna. Velit laoreet id donec ultrices tincidunt arcu non sodales. Amet justo donec enim diam vulputate ut pharetra sit. Odio facilisis mauris sit amet massa vitae."*/}
            {/*        />*/}
            {/*    </Col>*/}
            {/*</Row>*/}
            {/*<Row className="home-article">*/}
            {/*    <Col>*/}
            {/*        <Article*/}
            {/*            title="Local Cat Elected Mayor of Small Town"*/}
            {/*            img_src="/images/cat.jpg"*/}
            {/*            description="Foo bar baz qux quux corge grault garlpy waldo fred plugh xyzzy thud"*/}
            {/*        />*/}
            {/*    </Col>*/}
            {/*</Row>*/}
        </Container>
    );
};

export default Home;
