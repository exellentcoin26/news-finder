import { Card, Col, Row } from 'react-bootstrap';
import '../styles/Article.css';
import React, { useEffect, useState } from 'react';
import {
    ArticleApiResponse,
    ArticleSourceEntry,
} from '../interfaces/api/article';
import Dropdown from 'react-bootstrap/Dropdown';
import DropdownButton from 'react-bootstrap/DropdownButton';
import DropdownMenu from 'react-bootstrap/DropdownMenu';

function MyComponent() {
    const [isSmallScreen, setIsSmallScreen] = useState(window.innerWidth < 768);
    const [buttons, setButtons] = useState([
        'Het Laatste Nieuws',
        'vrt',
        'Gazet van Antwerpen',
        'Financial Times',
        'New York Times',
    ]);
    const visibleButtons = buttons.slice(0, 4);
    const hiddenButtons = buttons.slice(4);
    const showLoadMore = hiddenButtons.length > 0;
    const buttonCount = buttons.length;
    window.addEventListener('resize', () => {
        setIsSmallScreen(window.innerWidth < 768);
    });

    return (
        <div>
            {isSmallScreen ? (
                <DropdownButton
                    title="source"
                    drop="up"
                    size="sm"
                    menuVariant="dark"
                >
                    <DropdownMenu>
                        <Dropdown.Item className="drop-down-item-custom">
                            Het NiewsBlad
                        </Dropdown.Item>
                        <Dropdown.Item className="drop-down-item-custom">
                            De Gazet van Antwerpen
                        </Dropdown.Item>
                        <Dropdown.Item className="drop-down-item-custom">
                            vrt
                        </Dropdown.Item>
                        <Dropdown.Item className="drop-down-item-custom">
                            Het Laatste Nieuws
                        </Dropdown.Item>
                    </DropdownMenu>
                </DropdownButton>
            ) : (
                <div className="button-container">
                    {visibleButtons.map((button) => (
                        <button key={button} className="button">
                            {button}
                        </button>
                    ))}
                    {showLoadMore && <button className="button">. . .</button>}
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
    const [isSmallScreen, setIsSmallScreen] = useState(window.innerWidth < 768);

    window.addEventListener('resize', () => {
        setIsSmallScreen(window.innerWidth < 768);
    });
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
        <div>
            {isSmallScreen ? (
                <Col className="article-card">
                    <Col className="article-info">
                        <Row className="title-article">{title}</Row>
                        <Row className="article-body">{description}</Row>
                        <Row className="article-extra">
                            <Col className="clock-component-small">
                                <img
                                    src="/public/img/clock.png"
                                    className="clock"
                                ></img>
                                <p className="clock-text-small">3 hours ago</p>
                            </Col>
                            <Col className="sources-component">
                                <MyComponent></MyComponent>
                            </Col>
                        </Row>
                    </Col>
                    <Col>
                        <img
                            className="article-image w-full object-fit"
                            src={img_src ? img_src : '/img/no-image.png'}
                        ></img>
                    </Col>
                </Col>
            ) : (
                <Card className={'article-card'}>
                    <Row>
                        <a href={article_link}>
                            <Row className={'article-image'}>
                                <img
                                    src={
                                        img_src ? img_src : '/img/no-image.png'
                                    }
                                    style={
                                        img_src
                                            ? { objectFit: 'cover' }
                                            : { objectFit: 'contain' }
                                    }
                                />
                                <img />
                            </Row>
                        </a>
                        <Row>
                            <Card.Body className={'article-body'}>
                                <Card.Title>{title}</Card.Title>
                                <Card.Subtitle>
                                    Het Gazet van Antwerpen
                                </Card.Subtitle>
                                <Card.Body style={{ height: 'auto' }}>
                                    {description}
                                </Card.Body>
                                <div className="clock-component">
                                    <img
                                        src="/public/img/clock.png"
                                        width={15}
                                        className="clock"
                                    ></img>
                                    <p className="clock-text">3 hours ago</p>
                                </div>
                            </Card.Body>
                        </Row>
                    </Row>
                    <MyComponent></MyComponent>
                </Card>
            )}
        </div>
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
