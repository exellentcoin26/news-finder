import React, { useState } from 'react';
import { Container, Card, Form } from 'react-bootstrap';
import { Link } from 'react-router-dom';

import '../styles/Login-Register.css';
const Register = () => {
    const server_url =
        import.meta.env['VITE_SERVER_URL'] || 'http://localhost:5000';
    const target_url = server_url + '/user/';

    const handleRegister = async (username: string, password: string) => {
        await fetch(target_url, {
            method: 'POST',
            headers: { 'content-type': 'application/json' },
            body: JSON.stringify({ username: username, password: password }),
        });
    };

    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [passwordsMatch, setPasswordsMatch] = useState(true);

    React.useEffect(() => {
        validatePasswords();},
        [password, confirmPassword]
    );

    const validatePasswords = () => {
        password === confirmPassword
        ? setPasswordsMatch(true)
        : setPasswordsMatch(false)
    }

    return (
        <>
            <Container className="form-container center">
                <div>
                    <Card>
                        <Card.Body>
                            <div>
                                <h2 className="title mb-3"> Register Page </h2>
                            </div>
                            <div>
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
                                        aria-required = "true"
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
                                        aria-required= "true"
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
                                        {passwordsMatch? "" : "Passwords do not match"}
                                    </div>
                                </Form>
                            </div>
                            <div>
                                <button
                                    className="default-button sign-up-button mb-3"
                                    onClick={() =>
                                        handleRegister(username, password)
                                    }
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
                            </div>
                        </Card.Body>
                    </Card>
                </div>
            </Container>
        </>
    );
};

export default Register;
