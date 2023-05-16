import { Card, Col, Row } from 'react-bootstrap';
import '../styles/Article.css';
import React, { useEffect, useState } from 'react';
import {
    SimilarArticleApiResponse,
    SimilarArticleEntry,
} from '../interfaces/api/article';

function MyComponent() {
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

    return (
        <div>
            <div className="button-container">
                {visibleButtons.map((button) => (
                    <button key={button} className="button">
                        {button}
                    </button>
                ))}
                {showLoadMore && <button className="button">. . .</button>}
            </div>
        </div>
    );
}

const getSimilarArticlesFromServer = async (
    link: string,
): Promise<SimilarArticleEntry[]> => {
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

    const similarArticleApiResponse = ((): SimilarArticleApiResponse => {
        try {
            return JSON.parse(body);
        } catch (e) {
            console.debug(body);
            throw e;
        }
    })();

    if (similarArticleApiResponse.data == null) {
        // should always be caught with the error handler. This check is only needed for the type system.
        throw new Error('data property on `ArticleApiResponse` is not set');
    }

    return similarArticleApiResponse.data.articles.map((similarArticle) => {
        return similarArticle;
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
    const [similarArticles, setSimilarArticles] = useState<
        SimilarArticleEntry[]
    >([]);
    const [isSmallScreen, setIsSmallScreen] = useState(window.innerWidth < 768);
    const [open, setOpen] = useState(false);

    window.addEventListener('resize', () => {
        setIsSmallScreen(window.innerWidth < 768);
    });
    useEffect(() => {
        (async () => {
            try {
                const articles = await getSimilarArticlesFromServer(
                    article_link,
                );
                setSimilarArticles(articles);
            } catch (error) {
                console.error(error);
            }
        })();
    }, []);
    // Dropdown menu is based on the excellent tutorial from Kiet Vuong https://www.youtube.com/watch?v=KROfo7vuIGY
    return (
        <div>
            {isSmallScreen ? (
                <Col className="root-container">
                    <Row className="article-card">
                        <div className="clock-component-small">
                            <div>
                                <img
                                    src="/public/img/clock.png"
                                    className="clock"
                                ></img>
                            </div>
                            <p className="clock-text-small">36 minutes ago</p>
                        </div>
                        <Col className="article-info">
                            <Row>
                                <Row>
                                    <div className="menu-container">
                                        <div
                                            className="menu-trigger-button"
                                            onClick={() => {
                                                setOpen(!open);
                                            }}
                                        >
                                            <button className="menu-trigger">
                                                source
                                            </button>
                                        </div>
                                        <div
                                            className={`custom-dropdown-menu ${
                                                open ? 'active' : 'inactive'
                                            }`}
                                        >
                                            <ul>
                                                <DropdownItem
                                                    text={'Het Niewsblad'}
                                                />
                                                <DropdownItem
                                                    text={'Gazet van Antwerpen'}
                                                />
                                                <DropdownItem text={'vrt'} />
                                                <DropdownItem
                                                    text={'Financial Times'}
                                                />
                                            </ul>
                                        </div>
                                    </div>
                                </Row>
                                <Row className="article-title">{title}</Row>
                                <Row className="source_name-small">
                                    <p> Het Gazet Van antwerpen</p>
                                </Row>
                            </Row>
                        </Col>
                        <Col className="small-container-image">
                            <a href={article_link} className="article-link">
                                <img
                                    className="article-image"
                                    src={
                                        img_src ? img_src : '/img/no-image.png'
                                    }
                                ></img>
                            </a>
                        </Col>
                    </Row>
                </Col>
            ) : (
                <Card className={'article-card'}>
                    <Row>
                        <a href={article_link}>
                            <img
                                src={img_src ? img_src : '/img/no-image.png'}
                                className="article-image-img"
                                style={
                                    img_src
                                        ? { objectFit: 'cover' }
                                        : { objectFit: 'contain' }
                                }
                            />
                            <img />
                        </a>

                        <Row>
                            <Card.Body className={'article-body'}>
                                <Card.Title>{title}</Card.Title>
                                <p className="source_name-small">
                                    Het Gazet van Antwerpen
                                </p>
                                <Card.Body style={{ height: 'auto' }}>
                                    {description}
                                </Card.Body>
                                <div className="clock-component">
                                    <img
                                        src="/img/clock.png"
                                        width={15}
                                        className="clock"
                                    ></img>
                                    <p className="clock-text">32 minutes ago</p>
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

function DropdownItem(props: any) {
    return (
        <li className="dropdownItem">
            <a>{props.text}</a>
        </li>
    );
}
