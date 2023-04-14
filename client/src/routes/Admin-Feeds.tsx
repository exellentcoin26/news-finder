import Container from 'react-bootstrap/Container';
import { useEffect, useState } from 'react';
import Form from 'react-bootstrap/Form';
import Button from 'react-bootstrap/Button';
import { FeedsApiResponse, SourcesApiResponse } from '../interfaces/api/Rss';
import '../styles/Admin.css';
import { Simulate } from 'react-dom/test-utils';
import error = Simulate.error;

const server_url =
    import.meta.env['VITE_SERVER_URL'] || 'http://localhost:5000';

const getSourcesFromServer = async (): Promise<string[]> => {
    return fetch(server_url + '/source/', {
        method: 'GET',
        headers: { 'content-type': 'application/json' },
    })
        .then((response) => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then((data) => {
            const sources: SourcesApiResponse = data;
            return sources.sources;
        })
        .catch((error) => {
            console.error(error);
            return [];
        });
};

const getFeedsFromServer = async (source: string): Promise<string[]> => {
    if (!source) {
        return [];
    }
    return fetch(server_url + '/rss/by-source/', {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ source: source }),
    })
        .then((response) => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then((data) => {
            const feeds: FeedsApiResponse = data;
            return feeds.feeds;
        })
        .catch((error) => {
            console.log(error);
            return [];
        });
};

const Admin_Feeds = () => {
    const [inputFeeds, setInputFeeds] = useState<string>('');

    const [sources, setSources] = useState<string[]>([]);
    const [feeds, setFeeds] = useState<string[]>([]);
    const [selectedSource, setSelectedSource] = useState<string | null>(null);
    const [selectedFeed, setSelectedFeed] = useState<string | null>(null);

    useEffect(() => {
        getSourcesFromServer()
            .then((sources) => {
                setSources(sources);
                setSelectedSource(sources[0]!);
            })
            .then(() => getFeedsFromServer(sources[0]!))
            .then((feeds) => setFeeds(feeds))
            .then(() => setSelectedFeed(feeds[0]!))
            .catch((error) => {
                console.error(error);
                setSources([]);
            });
    }, []);

    useEffect(() => {
        if (selectedSource) {
            getFeedsFromServer(selectedSource)
                .then((feeds) => setFeeds(feeds))
                .then(() => setSelectedFeed(feeds[0]!))
                .catch((error) => console.error(error));
        } else {
            setFeeds([]);
        }
    }, [selectedSource]);

    const handleAddFeed = async (feeds: string): Promise<boolean> => {
        const array = feeds.split(';');

        const response = await fetch(server_url + '/rss/', {
            method: 'POST',
            headers: { 'content-type': 'application/json' },
            body: JSON.stringify({ feeds: array }),
        });

        return response.status == 200;
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

        return response.status == 200;
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
                        <Form.Select
                            onChange={(event) => {
                                setSelectedSource(event.target.value);
                            }}
                        >
                            {sources.map((option) => (
                                <option key={option}> {option} </option>
                            ))}
                        </Form.Select>
                    </Form.Group>
                    <Form.Group>
                        <Form.Select
                            onChange={(event) =>
                                setSelectedFeed(event.target.value)
                            }
                        >
                            {feeds.map((option) => (
                                <option key={option}> {option} </option>
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

export default Admin_Feeds;
