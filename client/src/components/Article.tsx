import { Card, Col, Row } from 'react-bootstrap';
import '../styles/Article.css';
import React, { useEffect, useState } from 'react';
import {
    SimilarArticleApiResponse,
    SimilarArticleEntry,
} from '../interfaces/api/article';
import { formatDistance } from 'date-fns';
import { SERVER_URL } from '../env';

function MyComponent({ currentArticleLink }: { currentArticleLink: string }) {
    const [similarArticles, setSimilarArticles] = useState<
        SimilarArticleEntry[]
    >([]);
    const visibleButtons = similarArticles.slice(0, 4);
    const hiddenButtons = similarArticles.slice(4);
    const showLoadMore = hiddenButtons.length > 0;

    useEffect(() => {
        (async () => {
            try {
                const articles = await getSimilarArticlesFromServer(
                    currentArticleLink,
                );
                setSimilarArticles(articles);
            } catch (error) {
                console.error(error);
            }
        })();
    }, []);

    return (
        <div>
            <div className="button-container">
                {similarArticles.map(({ source, link }, index) => {
                    return (
                        <>
                            {visibleButtons.map((article) => (
                                <button key={index} className="button">
                                    <a
                                        href={article.link}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                    >
                                        {' '}
                                        {article.source}{' '}
                                    </a>
                                </button>
                            ))}
                            {showLoadMore && (
                                <button className="button">. . .</button>
                            )}
                        </>
                    );
                })}
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
    source,
    timestamp,
}: {
    title: string;
    img_src?: string;
    description?: string;
    article_link: string;
    source: string;
    timestamp?: number;
}) => {
    const [isSmallScreen, setIsSmallScreen] = useState(window.innerWidth < 768);
    const [open, setOpen] = useState(false);
    const [similarArticles, setSimilarArticles] = useState<
        SimilarArticleEntry[]
    >([]);

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

    let timeAgo = '';
    if (timestamp) {
        const publication = new Date(timestamp * 1000);
        timeAgo = formatDistance(publication, new Date(), { addSuffix: true });
    }

    const handleArticleClick = async () => {
        const response = await fetch(SERVER_URL + '/user-history/', {
            method: 'POST',
            headers: { 'content-type': 'application/json' },
            body: JSON.stringify({
                articleLink: article_link,
            }),
            credentials: 'include',
        });

        if (!response.ok) throw Error('Failed to send server user history.');
    };

    // Dropdown menu is based on the excellent tutorial from Kiet Vuong https://www.youtube.com/watch?v=KROfo7vuIGY
    return (
        <div>
            {isSmallScreen ? (
                <Col className="root-container">
                    <Row className="article-card">
                        <div className="clock-component-small">
                            {timeAgo && (
                                <div className="clock-component">
                                    <img
                                        src="/img/clock.png"
                                        style={{ width: 15 }}
                                        className="clock"
                                    ></img>
                                    <p className="clock-text">{timeAgo}</p>
                                </div>
                            )}
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
                                                {similarArticles.map(
                                                    (
                                                        { source, link },
                                                        index,
                                                    ) => {
                                                        return (
                                                            <>
                                                                {similarArticles.map(
                                                                    (
                                                                        button,
                                                                    ) => (
                                                                        <DropdownItem
                                                                            key={
                                                                                index
                                                                            }
                                                                            className="button"
                                                                            text={
                                                                                button.source
                                                                            }
                                                                        >
                                                                            <a
                                                                                href={
                                                                                    link
                                                                                }
                                                                                target="_blank"
                                                                                rel="noopener noreferrer"
                                                                                onClick={
                                                                                    handleArticleClick
                                                                                }
                                                                            >
                                                                                {' '}
                                                                                {
                                                                                    source
                                                                                }{' '}
                                                                            </a>
                                                                        </DropdownItem>
                                                                    ),
                                                                )}
                                                            </>
                                                        );
                                                    },
                                                )}
                                            </ul>
                                        </div>
                                    </div>
                                </Row>
                                <Row className="article-title">{title}</Row>
                                <Row className="source_name-small">
                                    <a
                                        href={article_link}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        style={{
                                            color: 'inherit',
                                            textDecoration: 'none',
                                        }}
                                        onClick={handleArticleClick}
                                    >
                                        {source}
                                    </a>
                                </Row>
                            </Row>
                        </Col>
                        <Col className="small-container-image">
                            <a
                                href={article_link}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="article-link"
                                onClick={handleArticleClick}
                            >
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
                        <a
                            href={article_link}
                            target="_blank"
                            rel="noopener noreferrer"
                            onClick={handleArticleClick}
                        >
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
                                    <a
                                        href={article_link}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        style={{
                                            color: 'inherit',
                                            textDecoration: 'none',
                                        }}
                                        onClick={handleArticleClick}
                                    >
                                        {source}
                                    </a>
                                </p>
                                <Card.Body style={{ height: 'auto' }}>
                                    {description}
                                </Card.Body>
                                {timeAgo && (
                                    <div className="clock-component">
                                        <img
                                            src="/img/clock.png"
                                            style={{ width: 15 }}
                                            className="clock"
                                        ></img>
                                        <p className="clock-text">{timeAgo}</p>
                                    </div>
                                )}
                            </Card.Body>
                        </Row>
                    </Row>
                    <MyComponent
                        currentArticleLink={article_link}
                    ></MyComponent>
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
