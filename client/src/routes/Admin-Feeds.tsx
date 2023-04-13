import Container from 'react-bootstrap/Container';
import { useState } from 'react';
import Form from 'react-bootstrap/Form';
import Button from 'react-bootstrap/Button';
import '../styles/Admin.css';

const Admin_Feeds = () => {
    const server_url =
        import.meta.env['VITE_SERVER_URL'] || 'http://localhost:5000';

    const handleAddFeed = async (feeds: string): Promise<boolean> => {
        const array = feeds.split(';');

        const response = await fetch(server_url + '/rss/', {
            method: 'POST',
            headers: { 'content-type': 'application/json' },
            body: JSON.stringify({ feeds: array }),
        });

        return response.status == 200;
    };

    const [feeds, setFeeds] = useState('');
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
                            value={feeds}
                            onChange={(event) => setFeeds(event.target.value)}
                        ></Form.Control>
                    </Form.Group>
                    <Button
                        type="submit"
                        variant="custom"
                        onClick={() => handleAddFeed(feeds)}
                    >
                        Submit
                    </Button>
                </Form>
                <Container className="mb-5"></Container>
                <Form>
                    <Form.Group className="mb-3">
                        <Form.Label>Remove Feed</Form.Label>
                        <Form.Select>
                            <option>Temp1</option>
                            <option>Temp2</option>
                            <option>Temp3</option>
                        </Form.Select>
                    </Form.Group>
                    <Form.Group>
                        <Form.Select>
                            <option>Temp1</option>
                            <option>Temp2</option>
                            <option>Temp3</option>
                        </Form.Select>
                    </Form.Group>
                    <br />
                    <Button type="submit" variant="custom">
                        Remove
                    </Button>
                </Form>
            </Container>
        </Container>
    );
};

export default Admin_Feeds;
