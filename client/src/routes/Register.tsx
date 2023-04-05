import {Container, Card, Form} from "react-bootstrap";
import '../styles/Login-Register.css'
import {useState} from "react";

const Register = () => {

    const handleRegister = (username: string,password: string) => {
        fetch("/user/", {method: "POST", headers: {"content-type": "application.json"}, body: JSON.stringify({username: username, password: password})})
    }

    const [username, setUsername] = useState("")
    const [password, setPassword] = useState("")
    const [confirmPassword, setConfirmPassword] = useState("")

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
                                    <Form.Control required className="input-text mb-3" type="text" placeholder="Username" value={username} onChange={(event) => setUsername(event.target.value)}/>
                                    <Form.Control required className="input-text mb-3" type="password" placeholder="Password" value={password} onChange={(event) => setPassword(event.target.value)}/>
                                    <Form.Control required className="input-text mb-3" type="password" placeholder="Confirm Password" value={confirmPassword} onChange={(event) => setPassword(event.target.value)}/>
                                </Form>
                            </div>
                            <div>
                                <button className="default-button sign-up-button mb-3" onClick={() => handleRegister(username,password)}> Sign up </button>
                            </div>
                            <div>
                                <p className="normal-text"> Already have an account? </p>
                                <a href="/login">
                                    <button className="default-button link-button"> Log in </button>
                                </a>
                            </div>
                        </Card.Body>
                    </Card>
                </div>
            </Container>
        </>
    );
};

export default Register;
