import { Link } from 'react-router-dom';

const Navigation = () => {
    return (
        <ul role="nav">
            <li>
                <Link to="/home">Home</Link>
            </li>
            <li>
                <Link to="/login">Login</Link>
            </li>
            <li>
                <Link to="/register">Register</Link>
            </li>
        </ul>
    );
};

export default Navigation;
