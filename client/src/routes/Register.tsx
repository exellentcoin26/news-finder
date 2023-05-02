import { useState, useEffect } from 'react';
import { Container, Card, Form, Alert } from 'react-bootstrap';
import { Link, Navigate } from 'react-router-dom';

import { UserApiResponse } from '../interfaces/api/user';
import { ErrorKind } from '../interfaces/api/apiResponse';

import { SERVER_URL } from '../env';
import { isLoggedIn as checkLoggedIn } from '../helpers';

import '../styles/Login-Register.css';

interface RegisterStatusInfo {
    kind: RegisterStatusKind;
    message: string;
}

enum RegisterStatusKind {
    Success,
    Error,
}

const TARGET_URL = SERVER_URL + '/user/';

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
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [passwordsMatch, setPasswordsMatch] = useState(true);
    const [registerStatusInfo, setRegisterStatusInfo] = useState<
        RegisterStatusInfo[] | null
    >(null);
    const [isLoggedIn, setIsLoggedIn] = useState(false);

    useEffect(() => {
        setIsLoggedIn(checkLoggedIn());
    });

    const handleRegister = async (
        username: string,
        password: string,
        handleStatus: (status: RegisterStatusInfo[]) => void,
    ) => {
        const cleanUsername = username.trim();

        const errors = [];
        if (cleanUsername === '') {
            errors.push({
                kind: RegisterStatusKind.Error,
                message: 'Username cannot be empty',
            });
        }
        if (password === '') {
            errors.push({
                kind: RegisterStatusKind.Error,
                message: 'Password cannot be empty',
            });
        }
        if (errors.length > 1) {
            handleStatus(errors);
            return;
        }
        const response = await (async (): Promise<Response> => {
            try {
                return await fetch(TARGET_URL, {
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
                userApiResponse.errors.map(({ kind, message }) => {
                    if (
                        kind == ErrorKind.UserAlreadyPresent ||
                        message == 'User already in the databse'
                    ) {
                        message =
                            "This username isn't available. Please try another.";
                    }
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

    const handleRegisterStatus = (info: RegisterStatusInfo[]) => {
        setRegisterStatusInfo(info);

        // Reload page when login is successful
        info.map((info) => {
            if (info.kind == RegisterStatusKind.Success) location.reload();
        });
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
            {isLoggedIn ? (
                <Navigate replace to={'/home'} />
            ) : (
                <Container className="form-container container-fluid d-flex justify-content-center align-items-center">
                    <div className="form-div row d-flex align-items-center">
                        {registerStatusInfo ? (
                            <RegisterStatusBanner info={registerStatusInfo} />
                        ) : null}
                        <Card>
                            <Card.Body>
                                <h2 className="title mb-3"> Register </h2>
                                <Form>
                                    <Form.Control
                                        required
                                        className="input-text mb-3"
                                        type="text"
                                        placeholder="Username"
                                        value={username}
                                        onChange={(event) =>
                                            setUsername(event.target.value)
                                        }
                                        aria-required="true"
                                    />
                                    <Form.Control
                                        required
                                        className="input-text mb-3"
                                        type="password"
                                        placeholder="Password"
                                        value={password}
                                        onChange={(event) =>
                                            setPassword(event.target.value)
                                        }
                                        aria-required="true"
                                    />
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
                                    <div className="input-error">
                                        {passwordsMatch
                                            ? ''
                                            : 'Passwords do not match'}
                                    </div>
                                </Form>
                                <div className="float-start">
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
                            </Card.Body>
                        </Card>
                    </div>
                </Container>
            )}
        </>
    );
};

export default Register;
