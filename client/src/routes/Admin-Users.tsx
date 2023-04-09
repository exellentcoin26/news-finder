import '../styles/Admin.css';
import Container from 'react-bootstrap/Container';
import Form from 'react-bootstrap/Form';
import Button from 'react-bootstrap/Button';

const Admin_Users = () => {
    return (
        <Container>
            <Container className="page-title">User Management</Container>
            <Container>
                <Form>
                    <Form.Group className="mb-3">
                        <Form.Label>Remove Users</Form.Label>
                        <Form.Control placeholder="usernames"></Form.Control>
                    </Form.Group>
                    <Button type="submit">Submit</Button>
                </Form>
                <Container className="mb-5"></Container>
                <Form>
                    <Form.Group className="mb-3">
                        <Form.Label>Make Admin</Form.Label>
                        <Form.Control placeholder="usernames"></Form.Control>
                    </Form.Group>
                    <Button type="submit">Submit</Button>
                </Form>
            </Container>
        </Container>
    );
};

export default Admin_Users;
