import Container from 'react-bootstrap/Container';
import Col from 'react-bootstrap/Col';
import Row from 'react-bootstrap/Row';
import Article from '../components/Article';
import '../styles/Home.css';

const Home = () => {
    return (
        <Container className="home-container">
            <Row>
                <Col>
                    <Article
                        title="Local Cat Elected Mayor of Small Town"
                        img_src="/images/cat.jpg"
                        alt="Cat elected mayor"
                    />
                </Col>
                <Col>
                    <Article
                        title="Local Cat Elected Mayor of Small Town"
                        img_src="/images/cat.jpg"
                        alt="Cat elected mayor"
                    />
                </Col>
                <Col>
                    <Article
                        title="Local Cat Elected Mayor of Small Town"
                        img_src="/images/cat.jpg"
                        alt="Cat elected mayor"
                    />
                </Col>
            </Row>
        </Container>
    );
};

export default Home;
