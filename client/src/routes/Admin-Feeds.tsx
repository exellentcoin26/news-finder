import { Container, Form, Button } from 'react-bootstrap';
import React, { useEffect, useState } from 'react';
import { Navigate } from 'react-router-dom';

import { FeedsApiResponse, RssFeed } from '../interfaces/api/rss';
import { SourcesApiResponse } from '../interfaces/api/newsSource';

import { fetchAdminStatus } from '../helpers';
import { SERVER_URL } from '../env';

import '../styles/Admin.css';

const getSourcesFromServer = async () => {
    const response = await fetch(SERVER_URL + '/source/', {
        method: 'GET',
    });

    // TODO: Handle errors better

    if (response.ok) {
        const sources: SourcesApiResponse = await response.json();

        if (sources.data == null) {
            // should always be caught with the error handler. This check is only needed for the type system.
            throw new Error('data property on `SourceApiResponse` is not set');
        }

        return sources.data.sources;
        // TODO: Check json
    } else {
        throw new Error();
    }
};

const getFeedsFromServer = async (source: string): Promise<RssFeed[]> => {
    const response = await fetch(
        SERVER_URL + '/rss/?' + new URLSearchParams({ source: source }),
        {
            method: 'GET',
        },
    );

    if (response.ok) {
        const feeds: FeedsApiResponse = await response.json();

        if (feeds.data == null) {
            // should always be caught with the error handler. This check is only needed for the type system.
            throw new Error('data property on `FeedsApiResponse` is not set');
        }

        return feeds.data.feeds;
        // TODO: Check json
    } else {
        throw new Error();
    }
};

const AdminFeeds = () => {
    const [inputFeeds, setInputFeeds] = useState<string>('');
    const [category, setCategory] = useState<string>('');
    const [name, setName] = useState<string>('');

    const [sources, setSources] = useState<string[]>([]);
    const [feeds, setFeeds] = useState<RssFeed[]>([]);
    const [selectedSource, setSelectedSource] = useState<string | null>(null);
    const [selectedFeed, setSelectedFeed] = useState<string | null>(null);
    const [feedIsDisabled, setFeedIsDisabled] = useState<boolean>(true);
    const [isAdmin, setIsAdmin] = useState(false);
    const [isFetchingAdmin, setIsFetchingAdmin] = useState(true);

    // Admin guard
    useEffect(() => {
        (async () => {
            await fetchAdminStatus(setIsAdmin, setIsFetchingAdmin);
        })();
    });

    // Fetch sources
    useEffect(() => {
        (async () => {
            try {
                const sources = await getSourcesFromServer();
                setSources(sources);
            } catch (error) {
                console.log(error);
            }
        })();
    }, []);

    // Fetch feeds
    useEffect(() => {
        (async () => {
            if (selectedSource) {
                try {
                    const feeds = await getFeedsFromServer(selectedSource);
                    setFeeds(feeds);
                    setFeedIsDisabled(false);
                } catch (error) {
                    console.error(error);
                }
            } else {
                setFeeds([]);
                setFeedIsDisabled(true);
            }
        })();
    }, [selectedSource]);

    const handleSourceChange = (
        event: React.ChangeEvent<HTMLSelectElement>,
    ) => {
        setSelectedSource(event.target.value);
    };

    const handleFeedChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
        setSelectedFeed(event.target.value);
    };

    const handleAddFeed = async (
        name: string,
        feed: string,
        category: string,
    ): Promise<boolean> => {
        const response = await fetch(SERVER_URL + '/rss/', {
            method: 'POST',
            headers: { 'content-type': 'application/json' },
            body: JSON.stringify({
                name: name,
                feeds: feed,
                category: category,
            }),
        });

        if (response.ok) {
            window.alert('Successfully added rss feed(s)!');
        } else {
            window.alert('Could not add rss feed(s).');
        }

        return response.ok;
    };

    const handleRemoveFeed = async (feed: string | null): Promise<boolean> => {
        const confirmAction = window.confirm(
            `Do you want to remove feed \`${feed}\`?`,
        );

        if (!confirmAction) return false;

        if (feed == null) {
            return false;
        }

        const response = await fetch(SERVER_URL + '/rss/', {
            method: 'DELETE',
            headers: { 'content-type': 'application/json' },
            body: JSON.stringify({ feeds: [feed] }),
        });

        if (response.ok) {
            window.alert('Successfully removed rss feed!');
        } else {
            window.alert('Could not remove rss feed.');
        }

        return response.ok;
    };

    if (isFetchingAdmin) {
        return null;
    }

    if (!isAdmin) {
        return <Navigate replace to={'/home'} />;
    } else {
        return (
            <Container>
                <Container className="page-title">Feed Management</Container>
                <Container className="mb-5">
                    <Form>
                        <Form.Group className="mb-3">
                            <Form.Label>Add Feeds</Form.Label>
                            <Form.Control
                                type="text"
                                placeholder="feed"
                                value={inputFeeds}
                                onChange={(event) =>
                                    setInputFeeds(event.target.value)
                                }
                            ></Form.Control>
                        </Form.Group>
                        <Form.Group className="mb-3">
                            <Form.Control
                                type="text"
                                placeholder="category"
                                value={category}
                                onChange={(event) =>
                                    setCategory(event.target.value)
                                }
                            ></Form.Control>
                        </Form.Group>
                        <Form.Group className="mb-3">
                            <Form.Control
                                type="text"
                                placeholder="name"
                                value={name}
                                onChange={(event) =>
                                    setName(event.target.value)
                                }
                            ></Form.Control>
                        </Form.Group>
                        <Button
                            type="submit"
                            variant="custom"
                            onClick={(e) => {
                                e.preventDefault();
                                handleAddFeed(name, inputFeeds, category);
                            }}
                        >
                            Submit
                        </Button>
                    </Form>
                    <Container className="mb-5"></Container>
                    <Form>
                        <Form.Group className="mb-3">
                            <Form.Label>Remove Feed</Form.Label>
                            <Form.Select onChange={handleSourceChange}>
                                <option value="">Choose a source</option>
                                {sources.map((option) => (
                                    <option key={option} value={option}>
                                        {option}
                                    </option>
                                ))}
                            </Form.Select>
                        </Form.Group>
                        <Form.Group>
                            <Form.Select
                                onChange={handleFeedChange}
                                disabled={feedIsDisabled}
                            >
                                <option value="">Choose a feed</option>
                                {feeds.map(({ name, feed }) => (
                                    <option
                                        key={feed}
                                        value={feed + ' - ' + name}
                                    >
                                        {feed + ' - ' + name}
                                    </option>
                                ))}
                            </Form.Select>
                        </Form.Group>
                        <br />
                        <Button
                            type="submit"
                            variant="custom"
                            onClick={(e) => {
                                e.preventDefault();
                                handleRemoveFeed(selectedFeed);
                            }}
                        >
                            Remove
                        </Button>
                    </Form>
                </Container>
            </Container>
        );
    }
};

export default AdminFeeds;
