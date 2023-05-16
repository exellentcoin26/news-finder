import {
    Card,
    Row,
    Col,
    Popover,
    OverlayTrigger,
    ListGroup,
    ListGroupItem,
} from 'react-bootstrap';
import '../styles/Article.css';
import { useEffect, useState } from 'react';
import {
    ArticleApiResponse,
    ArticleSourceEntry,
} from '../interfaces/api/article';

const getSimilarArticlesFromServer = async (
    link: string,
): Promise<ArticleSourceEntry[]> => {
    const serverUrl =
        import.meta.env['VITE_SERVER_URL'] || 'http://localhost:5000';

    const response = await (async (): Promise<Response> => {
        try {
            return await fetch(
                serverUrl +
                    '/article/similar/?' +
                    new URLSearchParams({
                        url: link,
                    }),
            );
        } catch (e) {
            console.error(e);
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

    if (articleApiResponse.data == null) {
        // should always be caught with the error handler. This check is only needed for the type system.
        throw new Error('data property on `ArticleApiResponse` is not set');
    }

    return articleApiResponse.data.articles.map((articleSource) => {
        return articleSource;
    });
};

export const Article = ({
    title,
    img_src,
    description,
    article_link,
}: {
    title: string;
    img_src?: string;
    description?: string;
    article_link: string;
}) => {
    const [articles, setArticles] = useState<ArticleSourceEntry[]>([]);

    useEffect(() => {
        (async () => {
            try {
                const articles = await getSimilarArticlesFromServer(
                    article_link,
                );
                setArticles(articles);
            } catch (error) {
                console.error(error);
            }
        })();
    }, []);

    return (
        <Card className={'article-card'}>
            <Row md={1} className={'h-100'}>
                <Col className={'article-image'}>
                    <Card.Img
                        src={img_src ? img_src : '/img/no-image.png'}
                        className={'h-100'}
                        style={
                            img_src
                                ? { objectFit: 'cover' }
                                : { objectFit: 'contain' }
                        }
                    />
                </Col>
                <Col className={'h-100 '}>
                    <Card.Body
                        className={'article-body'}
                        style={{
                            overflow: 'hidden',
                        }}
                    >
                        <Card.Title>{title}</Card.Title>
                        <Card.Text>{description}</Card.Text>
                        <Card.Link
                            href={article_link}
                            target="_blank"
                            rel="noreferrer"
                        >
                            {' '}
                            Read full article{' '}
                        </Card.Link>
                        <OverlayTrigger
                            placement="right"
                            trigger="click"
                            overlay={
                                <Popover>
                                    {articles.length == 0 ? (
                                        <> No other news sources </>
                                    ) : (
                                        articles.map(
                                            ({ source, article }, index) => {
                                                return (
                                                    <ListGroup key={index}>
                                                        <ListGroupItem
                                                            href={article.link}
                                                        >
                                                            <p> {source} </p>
                                                        </ListGroupItem>
                                                    </ListGroup>
                                                );
                                            },
                                        )
                                    )}
                                </Popover>
                            }
                        >
                            <button className="similar-articles-button">
                                {' '}
                                show similar{' '}
                            </button>
                        </OverlayTrigger>
                    </Card.Body>
                </Col>
            </Row>
        </Card>
    );
};

export const ArticlePlaceholder = () => {
    return <h1>No articles loaded yet... Loading!</h1>;
};

export const NoArticlesToShow = () => {
    return <h1>No articles in database.</h1>;
};
