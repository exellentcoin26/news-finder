import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Alert, Card, Container, Form } from 'react-bootstrap';

import { UserApiResponse } from '../interfaces/api/user';

import '../styles/Login-Register.css';

interface LoginStatusInfo {
    kind: LoginStatusKind;
    message: string;
}

enum LoginStatusKind {
    Success,
    Error,
}

const LoginStatusBanner = ({ info }: { info: LoginStatusInfo[] }) => {
    return (
        <>
            {info.map(({ kind, message }, index) => (
                <Alert
                    variant={
                        kind == LoginStatusKind.Success ? 'success' : 'danger'
                    }
                    key={index}
                >
                    {message}
                </Alert>
            ))}
        </>
    );
};

const Login = () => {
    const server_url =
        import.meta.env['VITE_SERVER_URL'] || 'http://localhost:5000';
    const target_url = server_url + '/user/login/';

    const handleLogin = async (
        username: string,
        password: string,
        handleStatus: (status: LoginStatusInfo[]) => void,
    ) => {
        const cleanUsername = username.trim();

        const errors = [];
        if (cleanUsername === '') {
            errors.push({
                kind: LoginStatusKind.Error,
                message: 'Username cannot be empty',
            });
        }
        if (password === '') {
            errors.push({
                kind: LoginStatusKind.Error,
                message: 'Password cannot be empty',
            });
        }
        if (errors.length > 1) {
            handleStatus(errors);
            return;
        }
        const response = await (async (): Promise<Response> => {
            try {
                return await fetch(target_url, {
                    method: 'POST',
                    credentials: 'include',
                    headers: { 'content-type': 'application/json' },
                    body: JSON.stringify({
                        username: username,
                        password: password,
                    }),
                });
            } catch (e) {
                console.error(e);
                handleStatus([
                    {
                        kind: LoginStatusKind.Error,
                        message: 'Login request failed',
                    },
                ]);
                throw e;
            }
        })();

        const body = await response.text();

        const userApiResponse = ((): UserApiResponse => {
            try {
                return JSON.parse(body);
            } catch (e) {
                console.debug(body);
                throw e;
            }
        })();

        if (!response.ok) {
            handleStatus(
                userApiResponse.errors.map(({ message }) => {
                    return { kind: LoginStatusKind.Error, message };
                }),
            );
        } else {
            handleStatus([
                { kind: LoginStatusKind.Success, message: 'Login succeeded' },
            ]);
        }
    };

    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [loginStatusInfo, setLoginStatusInfo] = useState<
        LoginStatusInfo[] | null
    >(null);

    const handleLoginStatus = (info: LoginStatusInfo[]) => {
        setLoginStatusInfo(info);
    };

    return (
        <>
            <Container className="form-container center">
                {loginStatusInfo ? (
                    <LoginStatusBanner info={loginStatusInfo} />
                ) : null}
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
                                        handleLogin(
                                            username,
                                            password,
                                            handleLoginStatus,
                                        )
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
