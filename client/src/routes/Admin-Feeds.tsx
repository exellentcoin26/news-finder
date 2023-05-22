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
    const [inputFeeds, setInputFeeds] = useState<string | null>(null);
    const [category, setCategory] = useState<string | null>(null);
    const [name, setName] = useState<string | null>(null);
    const [interval, setInterval] = useState<number | null>(null);

    const [sources, setSources] = useState<string[]>([]);
    const [feeds, setFeeds] = useState<RssFeed[]>([]);
    const [selectedSource, setSelectedSource] = useState<string | null>(null);
    const [selectedFeed, setSelectedFeed] = useState<[string, string] | null>(
        null,
    );
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
        console.debug(event.target.options.selectedIndex);
        console.debug(feeds);
        // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
        const selected = feeds[event.target.options.selectedIndex - 1]!;
        setSelectedFeed([selected.feed, selected.name]);
    };

    const handleAddFeed = async (
        name: string,
        feed: string,
        category: string,
        interval: number | null,
    ): Promise<boolean> => {
        const response = await fetch(SERVER_URL + '/rss/', {
            method: 'POST',
            headers: { 'content-type': 'application/json' },
            body: JSON.stringify({
                name: name,
                feed: feed,
                category: category,
                ...(interval != null ? { interval: interval } : {}),
            }),
        });

        if (response.ok) {
            window.alert('Successfully added rss feed(s)!');
        } else {
            window.alert('Could not add rss feed(s).');
        }

        if (response.ok) location.reload();
        return response.ok;
    };

    const handleRemoveFeed = async (feed: string): Promise<boolean> => {
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

        if (response.ok) location.reload();
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
                        <Form.Label>Add Feeds</Form.Label>
                        <Form.Group className="mb-3">
                            <Form.FloatingLabel label={'feed'}>
                                <Form.Control
                                    type="text"
                                    {...(inputFeeds != null
                                        ? { value: inputFeeds }
                                        : {})}
                                    placeholder={'feed'}
                                    onChange={(event) =>
                                        setInputFeeds(event.target.value)
                                    }
                                />
                            </Form.FloatingLabel>
                        </Form.Group>
                        <Form.Group className="mb-3">
                            <Form.FloatingLabel label={'name'}>
                                <Form.Control
                                    type="text"
                                    {...(name != null ? { value: name } : {})}
                                    placeholder={'name'}
                                    onChange={(event) =>
                                        setName(event.target.value)
                                    }
                                />
                            </Form.FloatingLabel>
                        </Form.Group>
                        <Form.Group className="mb-3">
                            <Form.FloatingLabel label={'category'}>
                                <Form.Control
                                    type="text"
                                    {...(category != null
                                        ? { value: category }
                                        : {})}
                                    placeholder={'name'}
                                    onChange={(event) =>
                                        setCategory(event.target.value)
                                    }
                                />
                            </Form.FloatingLabel>
                        </Form.Group>
                        <Form.Group className="mb-3">
                            <Form.FloatingLabel
                                label={'scrape interval (minutes)'}
                            >
                                <Form.Control
                                    type="number"
                                    {...(interval != null
                                        ? { value: interval }
                                        : {})}
                                    placeholder={'interval'}
                                    onChange={(event) =>
                                        setInterval(
                                            Math.max(
                                                parseInt(event.target.value),
                                                1,
                                            ),
                                        )
                                    }
                                ></Form.Control>
                            </Form.FloatingLabel>
                        </Form.Group>
                        <Button
                            type="submit"
                            variant="custom"
                            onClick={(e) => {
                                e.preventDefault();
                                handleAddFeed(
                                    name || '',
                                    inputFeeds || '',
                                    category || '',
                                    interval,
                                );
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
                                const feed = selectedFeed?.[0];
                                if (feed === undefined)
                                    throw Error(
                                        'Feed should never be undefined',
                                    );
                                handleRemoveFeed(feed);
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
