import { Link } from 'react-router-dom';
import Container from 'react-bootstrap/Container';
import Navbar from 'react-bootstrap/Navbar';
import Nav from 'react-bootstrap/Nav';
import NavDropdown from 'react-bootstrap/NavDropdown';
import DropdownItem from 'react-bootstrap/DropdownItem';
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
                        <Nav.Link>
                            <Link to="/about" className="nav_text">
                                about
                            </Link>
                        </Nav.Link>
                    </Nav>
                    <Nav>
                        <NavDropdown
                            title={<span className="nav_text">admin</span>}
                            className="nav_text"
                        >
                            <DropdownItem>
                                <Nav.Link className="dropdown-nav-link">
                                    <Link
                                        to="/admin/users"
                                        className="dropdown-text"
                                    >
                                        users
                                    </Link>
                                </Nav.Link>
                            </DropdownItem>
                            <DropdownItem>
                                <Nav.Link className="dropdown-nav-link">
                                    <Link
                                        to="/admin/feeds"
                                        className="dropdown-text"
                                    >
                                        feeds
                                    </Link>
                                </Nav.Link>
                            </DropdownItem>
                        </NavDropdown>
                        <Nav.Link>
                            <Link to="/login" className="nav_text">
                                login
                            </Link>
                        </Nav.Link>
                    </Nav>
                </Navbar.Collapse>
            </Container>
        </Navbar>
    );
};

export default Navigation;
