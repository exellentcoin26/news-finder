import { Link } from 'react-router-dom';
import { Container, Navbar, Nav, NavDropdown, Dropdown } from 'react-bootstrap';
import { LinkContainer } from 'react-router-bootstrap';

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
                        <NavDropdown
                            title={<span className="nav_text">admin</span>}
                            className="nav_text"
                        >
                            <Dropdown.Item>
                                <Link
                                    to="/admin/users"
                                    className="dropdown-text dropdown-link"
                                >
                                    users
                                </Link>
                            </Dropdown.Item>
                            <Dropdown.Item>
                                <Link
                                    to="/admin/feeds"
                                    className="dropdown-text dropdown-link"
                                >
                                    feeds
                                </Link>
                            </Dropdown.Item>
                        </NavDropdown>
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
