import { Nav, Navbar, Container } from 'react-bootstrap';
import { LinkContainer } from 'react-router-bootstrap';
import { Link } from 'react-router-dom';

import '../styles/Navigation.css';

const Navigation = () => {
    return (
        <Navbar expand="lg" className="primary_color navbar-dark">
            <Container fluid>
                <Navbar.Brand>
                    <Link to="/home" className="home_text nav_text">
                        newsfinder
                    </Link>
                </Navbar.Brand>
                <Navbar.Toggle aria-controls="basic-navbar-nav" />
                <Navbar.Collapse id="basic-navbar-nav">
                    <Nav className="me-auto">
                        <LinkContainer to="/about">
                            <Nav.Link className="nav_text">about</Nav.Link>
                        </LinkContainer>
                    </Nav>
                    <Nav>
                        <LinkContainer to="/login">
                            <Nav.Link className="nav_text">login</Nav.Link>
                        </LinkContainer>
                    </Nav>
                </Navbar.Collapse>
            </Container>
        </Navbar>
    );
};

export default Navigation;
