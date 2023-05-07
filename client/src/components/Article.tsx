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

import React from 'react';
import Dropdown from 'react-bootstrap/Dropdown';
import DropdownButton from 'react-bootstrap/DropdownButton';

function MyComponent() {
    const [isSmallScreen, setIsSmallScreen] = useState(window.innerWidth < 768);

    window.addEventListener('resize', () => {
        setIsSmallScreen(window.innerWidth < 768);
    });

    return (
        <div>
            {isSmallScreen ? (
                <DropdownButton
                    title="source"
                    className="Drop-down-button-custom"
                >
                    <Dropdown.Item className="drop-down-item-custom">
                        Action
                    </Dropdown.Item>
                    <Dropdown.Item>Another action</Dropdown.Item>
                    <Dropdown.Item>Something else</Dropdown.Item>
                </DropdownButton>
            ) : (
                <div className="button-container">
                    <button className="button">Het NiewsBlad</button>
                    <button className="button">De Gazet van Antwerpen</button>
                    <button className="button">vrt</button>
                </div>
            )}
        </div>
    );
}

const getSimilarArticlesFromServer = async (
    link: string,
): Promise<ArticleSourceEntry[]> => {
    const serverUrl =
        import.meta.env['VITE_SERVER_URL'] || 'http://localhost:5000';

    const response = await (async (): Promise<Response> => {
        try {
            return await fetch(
                serverUrl +
                    '/article/similar?' +
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
            <Row md={1} className={'h-50'}>
                <a href={article_link}>
                    <Row className={'article-image'}>
                        <Card.Img
                            src={img_src ? img_src : '/img/no-image.png'}
                            className={'h-100'}
                            style={
                                img_src
                                    ? { objectFit: 'cover' }
                                    : { objectFit: 'contain' }
                            }
                        />
                    </Row>
                </a>

                <Row className={'h-100 '}>
                    <Card.Body
                        className={'flex-grow-1'}
                        style={{
                            overflow: 'hidden',
                        }}
                    >
                        <Card.Title>{title}</Card.Title>
                        <Card.Text style={{ height: 'auto' }}>
                            {description}
                        </Card.Text>
                        <MyComponent />
                        <div className="clock-text">3 hours ago</div>
                    </Card.Body>
                </Row>
            </Row>
        </Card>
    );
};

export const ArticlePlaceholder = () => {
    return <h1>No articles loaded yet... Loading!</h1>;
};

export default function LoadingSpinner() {
    return (
        <div className="spinner-container">
            <div className="loading-spinner"></div>
        </div>
    );
}

export const NoArticlesToShow = () => {
    return <h1>No articles in database.</h1>;
};
