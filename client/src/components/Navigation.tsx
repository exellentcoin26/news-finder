import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Container, Navbar, Nav, NavDropdown, Dropdown } from 'react-bootstrap';
import { LinkContainer } from 'react-router-bootstrap';

import {
    fetchAdminStatus,
    isLoggedIn as checkLoggedIn,
    logout,
} from '../helpers';

import '../styles/Navigation.css';

const Navigation = () => {
    const [isAdmin, setAdminStatus] = useState<boolean>(false);
    const [isLoggedIn, setIsLoggedIn] = useState<boolean>(false);

    useEffect(() => {
        (async () => {
            setIsLoggedIn(checkLoggedIn());
            await fetchAdminStatus(setAdminStatus, () => undefined);
        })();
    }, []);

    return (
        <Navbar expand="lg" className="primary_color navbar-dark">
            <Container fluid>
                <Navbar.Brand>
                    <Link to="/home" className="home-text nav-text">
                        <img
                            src="/img/favicon.ico"
                            alt=""
                            className="nav-icon"
                        />
                        newsfinder
                    </Link>
                </Navbar.Brand>
                <Navbar.Toggle aria-controls="basic-navbar-nav" />
                <Navbar.Collapse id="basic-navbar-nav">
                    <Nav className="me-auto">
                        <LinkContainer to="/about">
                            <Nav.Link className="nav-text">about</Nav.Link>
                        </LinkContainer>
                    </Nav>
                    <Nav>
                        {isAdmin && (
                            <NavDropdown
                                title={<span className="nav-text">admin</span>}
                                className="nav-text"
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
                        )}
                        {isLoggedIn ? (
                            <Nav.Link onClick={logout} className="nav-text">
                                logout
                            </Nav.Link>
                        ) : (
                            <LinkContainer to="/login">
                                <Nav.Link className="nav-text">login</Nav.Link>
                            </LinkContainer>
                        )}
                    </Nav>
                </Navbar.Collapse>
            </Container>
        </Navbar>
    );
};

export default Navigation;
