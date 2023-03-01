import { Link } from 'react-router-dom';
import Container from 'react-bootstrap/Container';
import Navbar from 'react-bootstrap/Navbar';
import Nav from 'react-bootstrap/Nav';
import NavDropdown from 'react-bootstrap/NavDropdown';
import '../../public/styles/Navbar.css';

const Navigation = () => {
    return (
        // <ul role="nav">
        //     <li>
        //         <Link to="/home">Home</Link>
        //     </li>
        //     <li>
        //         <Link to="/login">Login</Link>
        //     </li>
        //     <li>
        //         <Link to="/register">Register</Link>
        //     </li>
        // </ul>
        <Navbar expand="lg" className="primary_color">
            <Container>
                <Navbar.Brand>
                    <Link to="/home">newsfinder</Link>
                </Navbar.Brand>
                <Navbar.Toggle aria-controls="basic-navbar-nav" />
                <Navbar.Collapse id="basic-navbar-nav">
                    <Nav className="me-auto">
                        <Nav.Link>
                            <Link to="/login">
                                <Container className="secondary_color menu_rounding">
                                    login
                                </Container>
                            </Link>
                        </Nav.Link>
                        <Nav.Link>
                            <Link to="/register">register</Link>
                        </Nav.Link>
                    </Nav>
                </Navbar.Collapse>
            </Container>
        </Navbar>
    );
};

export default Navigation;
