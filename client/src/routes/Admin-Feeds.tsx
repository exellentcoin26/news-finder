import Container from 'react-bootstrap/Container';
import Form from 'react-bootstrap/Form';
import Button from 'react-bootstrap/Button';
import '../styles/Admin.css';

const Admin_Feeds = () => {
    return (
        <Container>
            <Container className="page-title">Feed Management</Container>
            <Container>
                <Form>
                    <Form.Group className="mb-3">
                        <Form.Label>Add Feeds</Form.Label>
                        <Form.Control placeholder="feeds"></Form.Control>
                    </Form.Group>
                    <Button type="submit" variant="custom">
                        Submit
                    </Button>
                </Form>
                <Container className="mb-5"></Container>
                <Form>
                    <Form.Group className="mb-3">
                        <Form.Label>Remove Feed</Form.Label>
                        <Form.Select>
                            <option>Temp1</option>
                            <option>Temp2</option>
                            <option>Temp3</option>
                        </Form.Select>
                    </Form.Group>
                    <Form.Group>
                        <Form.Select>
                            <option>Temp1</option>
                            <option>Temp2</option>
                            <option>Temp3</option>
                        </Form.Select>
                    </Form.Group>
                    <br />
                    <Button type="submit" variant="custom">
                        Remove
                    </Button>
                </Form>
            </Container>
        </Container>
    );
};

export default Admin_Feeds;
