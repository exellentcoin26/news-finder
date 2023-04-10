import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Container, Card, Form } from 'react-bootstrap';

import '../styles/Login-Register.css';

const Login = () => {
    const server_url =
        import.meta.env['VITE_SERVER_URL'] || 'http://localhost:5000';
    const target_url = server_url + '/user/login/';

    const handleLogin = async (username: string, password: string) => {
        await fetch(target_url, {
            method: 'POST',
            credentials: 'include',
            headers: { 'content-type': 'application/json' },
            body: JSON.stringify({ username: username, password: password }),
        });
    };

    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');

    return (
        <>
            <Container className="form-container center">
                <div>
                    <Card>
                        <Card.Body>
                            <div>
                                <h2 className="title mb-3"> Login </h2>
                            </div>
                            <div>
                                <Form>
                                    <Form.Control
                                        className="input-text mb-3"
                                        type="text"
                                        placeholder="Username"
                                        value={username}
                                        onChange={(event) =>
                                            setUsername(event.target.value)
                                        }
                                    />
                                    <Form.Control
                                        className="input-text mb-3"
                                        type="password"
                                        placeholder="Password"
                                        value={password}
                                        onChange={(event) =>
                                            setPassword(event.target.value)
                                        }
                                    />
                                </Form>
                            </div>
                            <div>
                                <Link to="/register">
                                    <button className="default-button link-button mb-3">
                                        {' '}
                                        Create an account{' '}
                                    </button>
                                </Link>
                                <button
                                    className="default-button login-button mb-3"
                                    onClick={() =>
                                        handleLogin(username, password)
                                    }
                                >
                                    {' '}
                                    Login{' '}
                                </button>
                            </div>
                        </Card.Body>
                    </Card>
                </div>
            </Container>
        </>
    );
};

export default Login;
