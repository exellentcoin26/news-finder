import Container from 'react-bootstrap/Container';
import { useState } from 'react';
import Form from 'react-bootstrap/Form';
import Button from 'react-bootstrap/Button';
import '../styles/Admin.css';

const Admin_Users = () => {
    const server_url =
        import.meta.env['VITE_SERVER_URL'] || 'http://localhost:5000';
    const target_url = server_url + '/user/';

    const handleUserDeletion = async (username: string): Promise<boolean> => {
        const response = await fetch(target_url, {
            method: 'DELETE',
            headers: { 'content-type': 'application/json' },
            body: JSON.stringify({ username: username }),
        });

        return response.status == 200;
    };

    const [usernameDelete, setUsernameDelete] = useState('');
    const [usernameMakeAdmin, setUsernameMakeAdmin] = useState('');

    return (
        <Container>
            <Container className="page-title">User Management</Container>
            <Container>
                <Form>
                    <Form.Group className="mb-3">
                        <Form.Label>Remove Users</Form.Label>
                        <Form.Control
                            type="text"
                            placeholder="username"
                            value={usernameDelete}
                            onChange={(event) =>
                                setUsernameDelete(event.target.value)
                            }
                        ></Form.Control>
                    </Form.Group>
                    <Button
                        type="submit"
                        variant="custom"
                        onClick={() => handleUserDeletion(usernameDelete)}
                    >
                        Remove
                    </Button>
                </Form>
                <Container className="mb-5"></Container>
                <Form>
                    <Form.Group className="mb-3">
                        <Form.Label>Make Admin</Form.Label>
                        <Form.Control
                            type="text"
                            placeholder="usernames"
                            value={usernameMakeAdmin}
                            onChange={(event) =>
                                setUsernameMakeAdmin(event.target.value)
                            }
                        ></Form.Control>
                    </Form.Group>
                    <Button type="submit" variant="custom">
                        Submit
                    </Button>
                </Form>
            </Container>
        </Container>
    );
};

export default Admin_Users;
