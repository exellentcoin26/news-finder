import { Container, Form, Button } from 'react-bootstrap';
import { useEffect, useState } from 'react';

import { Navigate } from 'react-router-dom';

import { fetchAdminStatus } from '../helpers';
import { SERVER_URL } from '../env';

import '../styles/Admin.css';

const AdminUsers = () => {
    const [usernameDelete, setUsernameDelete] = useState('');
    const [usernameMakeAdmin, setUsernameMakeAdmin] = useState('');
    const [isAdmin, setIsAdmin] = useState(false);
    const [isFetchingAdmin, setIsFetchingAdmin] = useState(true);

    // Admin guard
    useEffect(() => {
        (async () => {
            await fetchAdminStatus(setIsAdmin, setIsFetchingAdmin);
        })();
    }, []);

    const handleUserDeletion = async (username: string): Promise<boolean> => {
        const response = await fetch(SERVER_URL + '/user/', {
            method: 'DELETE',
            headers: { 'content-type': 'application/json' },
            body: JSON.stringify({ username: username }),
        });

        return response.ok;
    };

    const handleMakeAdmin = async (username: string): Promise<boolean> => {
        const response = await fetch(SERVER_URL + '/admin/', {
            method: 'POST',
            headers: { 'content-type': 'application/json' },
            body: JSON.stringify({ usernames: [username] }),
        });

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
                <Container className="page-title">User Management</Container>
                <Container>
                    <Form>
                        <Form.Group className="mb-3">
                            <Form.Label>Remove Users</Form.Label>
                            <Form.Control
                                type="text"
                                placeholder="username"
                                value={usernameDelete}
                                onChange={async (event) =>
                                    setUsernameDelete(event.target.value)
                                }
                            ></Form.Control>
                        </Form.Group>
                        <Button
                            type="submit"
                            variant="custom"
                            onClick={(e) => {
                                e.preventDefault();
                                handleUserDeletion(usernameDelete);
                            }}
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
                                placeholder="username"
                                value={usernameMakeAdmin}
                                onChange={(event) =>
                                    setUsernameMakeAdmin(event.target.value)
                                }
                            ></Form.Control>
                        </Form.Group>
                        <Button
                            type="submit"
                            variant="custom"
                            onClick={(e) => {
                                e.preventDefault();
                                handleMakeAdmin(usernameMakeAdmin);
                            }}
                        >
                            Submit
                        </Button>
                    </Form>
                </Container>
            </Container>
        );
    }
};

export default AdminUsers;
