import { useState, useEffect } from 'react';
import { Container, Card, Form, Alert } from 'react-bootstrap';
import { Link } from 'react-router-dom';

import { UserApiResponse } from '../interfaces/api/user';

import '../styles/Login-Register.css';

interface RegisterStatusInfo {
    kind: RegisterStatusKind;
    message: string;
}

enum RegisterStatusKind {
    Success,
    Error,
}

const RegisterStatusBanner = ({ info }: { info: RegisterStatusInfo[] }) => {
    return (
        <>
            {info.map(({ kind, message }, index) => (
                <Alert
                    variant={
                        kind == RegisterStatusKind.Success
                            ? 'success'
                            : 'danger'
                    }
                    key={index}
                >
                    {message}
                </Alert>
            ))}
        </>
    );
};

const Register = () => {
    const server_url =
        import.meta.env['VITE_SERVER_URL'] || 'http://localhost:5000';
    const target_url = server_url + '/user/';

    const handleRegister = async (
        username: string,
        password: string,
        handleStatus: (status: RegisterStatusInfo[]) => void,
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
                        kind: RegisterStatusKind.Error,
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
                    return { kind: RegisterStatusKind.Error, message };
                }),
            );
        } else {
            handleStatus([
                {
                    kind: RegisterStatusKind.Success,
                    message: 'Register succeeded',
                },
            ]);
        }
    };

    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [passwordsMatch, setPasswordsMatch] = useState(true);
    const [registerStatusInfo, setRegisterStatusInfo] = useState<
        RegisterStatusInfo[] | null
    >(null);

    const handleRegisterStatus = (info: RegisterStatusInfo[]) => {
        setRegisterStatusInfo(info);
    };

    useEffect(() => {
        validatePasswords();
    }, [password, confirmPassword]);

    const validatePasswords = () => {
        password === confirmPassword
            ? setPasswordsMatch(true)
            : setPasswordsMatch(false);
    };

    return (
        <>
            <Container className="form-container container-fluid d-flex justify-content-center align-items-center">
                {registerStatusInfo ? (
                    <RegisterStatusBanner info={registerStatusInfo} />
                ) : null}
                <div className="form-div row d-flex align-items-center">
                    <Card>
                        <Card.Body>
                            <div>
                                <h2 className="title mb-3"> Register </h2>
                            </div>
                            <div>
                                <Form>
                                    <div>
                                        <Form.Control
                                            required
                                            className="input-text mb-3"
                                            type="text"
                                            placeholder="Username"
                                            value={username}
                                            onChange={(event) =>
                                                setUsername(event.target.value)
                                            }
                                            aria-required = "true"
                                        />
                                    </div>
                                    <div>
                                        <Form.Control
                                            required
                                            className="input-text mb-3"
                                            type="password"
                                            placeholder="Password"
                                            value={password}
                                            onChange={(event) =>
                                                setPassword(event.target.value)
                                            }
                                            aria-required= "true"
                                        />
                                    </div>
                                    <div>
                                        <Form.Control
                                            required
                                            className="input-text mb-3"
                                            type="password"
                                            placeholder="Confirm Password"
                                            value={confirmPassword}
                                            onChange={(event) =>
                                                setConfirmPassword(
                                                    event.target.value,
                                                )
                                            }
                                            aria-required="true"
                                            aria-invalid={passwordsMatch}
                                        />
                                    </div>
                                    <div className="input-error">
                                        {passwordsMatch
                                            ? ''
                                            : 'Passwords do not match'}
                                    </div>
                                </Form>
                            </div>
                            <div>
                                <button
                                    className="default-button sign-up-button mb-3"
                                    onClick={() => {
                                        if (!passwordsMatch) return;
                                        handleRegister(
                                            username,
                                            password,
                                            handleRegisterStatus,
                                        );
                                    }}
                                >
                                    {' '}
                                    Sign up{' '}
                                </button>
                            </div>
                            <div>
                                <p className="normal-text">
                                    {' '}
                                    Already have an account?{' '}
                                </p>
                                <Link to="/login">
                                    <button className="default-button link-button">
                                        {' '}
                                        Log in{' '}
                                    </button>
                                </Link>
                                <div>
                                    <p className="normal-text">
                                        {' '}
                                        Already have an account?{' '}
                                    </p>
                                    <Link to="/login">
                                        <button className="default-button link-button">
                                            {' '}
                                            Log in{' '}
                                        </button>
                                    </Link>
                                    <button
                                        className="default-button sign-up-button mb-3"
                                        onClick={() => {
                                            if (!passwordsMatch) return
                                            handleRegister(
                                                username,
                                                password,
                                                handleRegisterStatus,
                                            )}
                                        }
                                    >
                                        {' '}
                                        Sign up{' '}
                                    </button>
                                </div>
                            </div>
                        </Card.Body>
                    </Card>
                </div>
            </Container>
        </>
    );
};

export default Register;
