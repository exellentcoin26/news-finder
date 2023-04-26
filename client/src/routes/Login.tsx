import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Container, Card, Form, Alert } from 'react-bootstrap';

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
            <Container className="form-container container-fluid d-flex justify-content-center align-items-center">
                <div className="form-div row d-flex align-items-center">
                    <div>
                        {loginStatusInfo ? (
                            <LoginStatusBanner info={loginStatusInfo} />
                        ) : null}
                    </div>
                    <div>
                        <Card>
                            <Card.Body>
                                <div>
                                    <h2 className="title mb-3"> Login </h2>
                                </div>
                                <div>
                                    <Form>
                                        <div>
                                            <Form.Group>
                                                <div>
                                                    <Form.Control
                                                        className="input-text mb-3"
                                                        type="text"
                                                        placeholder="Username"
                                                        value={username}
                                                        onChange={(event) =>
                                                            setUsername(event.target.value)
                                                        }
                                                    />
                                                </div>
                                            </Form.Group>
                                        </div>
                                        <div>
                                            <Form.Group>
                                                <div>
                                                    <Form.Control
                                                        className="input-text mb-3"
                                                        type="password"
                                                        placeholder="Password"
                                                        value={password}
                                                        onChange={(event) =>
                                                            setPassword(event.target.value)
                                                        }
                                                    />
                                                </div>
                                            </Form.Group>
                                        </div>
                                    </Form>
                                </div>
                                <div>
                                    <div className="float-start">
                                        <Link to="/register">
                                            <button className="default-button link-button mb-3">
                                                {' '}
                                                Create an account{' '}
                                            </button>
                                        </Link>
                                    </div>
                                    <div className="float-end">
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

                                </div>
                            </Card.Body>
                        </Card>
                    </div>
                </div>
            </Container>
        </>
    );
};

export default Login;
