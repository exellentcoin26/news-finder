import Container from 'react-bootstrap/Container';
import { useEffect, useState } from 'react';
import Form from 'react-bootstrap/Form';
import Button from 'react-bootstrap/Button';
import { AdminStatusApiResponse } from '../interfaces/api/admin';
import { Navigate } from 'react-router-dom';
import '../styles/Admin.css';

const AdminUsers = () => {
    const server_url =
        import.meta.env['VITE_SERVER_URL'] || 'http://localhost:5000';

    const handleUserDeletion = async (username: string): Promise<boolean> => {
        const response = await fetch(server_url + '/user/', {
            method: 'DELETE',
            headers: { 'content-type': 'application/json' },
            body: JSON.stringify({ username: username }),
        });

        return response.ok;
    };

    const handleMakeAdmin = async (username: string): Promise<boolean> => {
        const response = await fetch(server_url + '/admin/', {
            method: 'POST',
            headers: { 'content-type': 'application/json' },
            body: JSON.stringify({ usernames: [username] }),
        });

        return response.ok;
    };

    useEffect(() => {
        const fetchAdminStatus = async () => {
            const response = await fetch(server_url + '/admin/', {
                method: 'GET',
                credentials: 'include',
            });

            const adminStatusApiResponse: AdminStatusApiResponse =
                await response.json();

            if (adminStatusApiResponse.data == null) {
                throw new Error(
                    'data property on `AdminStatusApiResponse` object',
                );
            }

            if (adminStatusApiResponse.data.admin) {
                setIsAdmin(true);
            } else {
                setIsAdmin(false);
            }
            setIsFetchingAdmin(false);
        };

        fetchAdminStatus();
    }, []);

    const [usernameDelete, setUsernameDelete] = useState('');
    const [usernameMakeAdmin, setUsernameMakeAdmin] = useState('');
    const [isAdmin, setIsAdmin] = useState(false);
    const [isFetchingAdmin, setIsFetchingAdmin] = useState(true);

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
