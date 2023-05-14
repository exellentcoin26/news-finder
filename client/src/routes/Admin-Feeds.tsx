import {
    Container,
    Form,
    Button,
    Popover,
    OverlayTrigger,
} from 'react-bootstrap';
import React, { useEffect, useState } from 'react';
import { Navigate } from 'react-router-dom';

import { FeedsApiResponse } from '../interfaces/api/rss';
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

const getFeedsFromServer = async (source: string) => {
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

    const [sources, setSources] = useState<string[]>([]);
    const [feeds, setFeeds] = useState<string[]>([]);
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

    const handleAddFeed = async (feeds: string, category: string): Promise<boolean> => {
        const array = feeds
            .split(';' || ' ')
            .map((feed) => feed.trim())
            .filter((str) => str.length !== 0);

        const response = await fetch(SERVER_URL + '/rss/', {
            method: 'POST',
            headers: { 'content-type': 'application/json' },
            body: JSON.stringify({ feeds: array, category: category}),
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

    const addHelp = (
        <Popover id="popover-add-help">
            <Popover.Header as="h3">Add feeds</Popover.Header>
            <Popover.Body>
                Add several feeds at once by separating them with a
                &apos;;&apos;
            </Popover.Body>
        </Popover>
    );

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
                            <Form.Label>
                                Add Feeds
                                <OverlayTrigger
                                    trigger="hover"
                                    overlay={addHelp}
                                    placement="bottom"
                                >
                                    <Button variant="light help-button">
                                        <img
                                            src="../../public/img/question-circle.svg"
                                            alt="?"
                                        />
                                    </Button>
                                </OverlayTrigger>
                            </Form.Label>
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
                            >
                            </Form.Control>
                        </Form.Group>
                        <Button
                            type="submit"
                            variant="custom"
                            onClick={(e) => {
                                e.preventDefault();
                                handleAddFeed(inputFeeds, category);
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
                                {feeds.map((option) => (
                                    <option key={option} value={option}>
                                        {option}
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
