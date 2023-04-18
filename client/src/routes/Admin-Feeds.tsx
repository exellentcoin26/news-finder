import Container from 'react-bootstrap/Container';
import React, { useEffect, useState } from 'react';
import Form from 'react-bootstrap/Form';
import Button from 'react-bootstrap/Button';
import { FeedsApiResponse } from '../interfaces/api/rss';
import { SourcesApiResponse } from '../interfaces/api/newsSource';

import '../styles/Admin.css';

const server_url =
    import.meta.env['VITE_SERVER_URL'] || 'http://localhost:5000';

const getSourcesFromServer = async () => {
    const response = await fetch(server_url + '/source/', {
        method: 'GET',
        headers: { 'content-type': 'application/json' },
    });

    if (response.ok) {
        const sources: SourcesApiResponse = await response.json();
        return sources.data.sources;
        // TODO: Check json
    } else {
        throw new Error();
    }
};

const getFeedsFromServer = async (source: string) => {
    const response = await fetch(
        server_url + '/rss/?' + new URLSearchParams({ source: source }),
        {
            method: 'GET',
            headers: { 'content-type': 'application/json' },
        },
    );

    if (response.ok) {
        const feeds: FeedsApiResponse = await response.json();
        return feeds.data.feeds;
        // TODO: Check json
    } else {
        throw new Error();
    }
};

const AdminFeeds = () => {
    const [inputFeeds, setInputFeeds] = useState<string>('');

    const [sources, setSources] = useState<string[]>([]);
    const [feeds, setFeeds] = useState<string[]>([]);
    const [selectedSource, setSelectedSource] = useState<string | null>(null);
    const [selectedFeed, setSelectedFeed] = useState<string | null>(null);
    const [feedIsDisabled, setFeedIsDisabled] = useState<boolean>(true);

    useEffect(() => {
        const fetchSources = async () => {
            try {
                const sources = await getSourcesFromServer();
                setSources(sources);
            } catch (error) {
                console.log(error);
            }
        };

        fetchSources();
    }, []);

    useEffect(() => {
        const fetchFeeds = async () => {
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
        };

        fetchFeeds();
    }, [selectedSource]);

    const handleSourceChange = (
        event: React.ChangeEvent<HTMLSelectElement>,
    ) => {
        setSelectedSource(event.target.value);
    };

    const handleFeedChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
        setSelectedFeed(event.target.value);
    };

    const handleAddFeed = async (feeds: string): Promise<boolean> => {
        const array = feeds
            .split(';' || ' ')
            .map((feed) => feed.trim())
            .filter((str) => str.length !== 0);

        const response = await fetch(server_url + '/rss/', {
            method: 'POST',
            headers: { 'content-type': 'application/json' },
            body: JSON.stringify({ feeds: array }),
        });

        return response.ok;
    };

    const handleRemoveFeed = async (feed: string | null): Promise<boolean> => {
        if (feed == null) {
            return false;
        }
        const response = await fetch(server_url + '/rss/', {
            method: 'DELETE',
            headers: { 'content-type': 'application/json' },
            body: JSON.stringify({ feeds: [feed] }),
        });

        return response.ok;
    };

    return (
        <Container>
            <Container className="page-title">Feed Management</Container>
            <Container>
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
                    <Button
                        type="submit"
                        variant="custom"
                        onClick={() => handleAddFeed(inputFeeds)}
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
                        onClick={() => {
                            handleRemoveFeed(selectedFeed);
                        }}
                    >
                        Remove
                    </Button>
                </Form>
            </Container>
        </Container>
    );
};

export default AdminFeeds;
