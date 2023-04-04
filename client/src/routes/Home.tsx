import Container from 'react-bootstrap/Container';
import Col from 'react-bootstrap/Col';
import Row from 'react-bootstrap/Row';
import Article from '../components/Article';
import '../styles/Home.css';

const Home = () => {
    return (
        <Container className="home-container">
            <Row className="home-article">
                <Col>
                    <Article
                        title="Local Cat Elected Mayor of Small Town"
                        img_src="/images/cat.jpg"
                        description="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
                    />
                </Col>
            </Row>
            <Row className="home-article">
                <Col>
                    <Article
                        title="Local Cat Elected Mayor of Small Town"
                        img_src="/images/cat.jpg"
                        description="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Sem fringilla ut morbi tincidunt. Faucibus interdum posuere lorem ipsum dolor. Pellentesque dignissim enim sit amet venenatis urna. Velit laoreet id donec ultrices tincidunt arcu non sodales. Amet justo donec enim diam vulputate ut pharetra sit. Odio facilisis mauris sit amet massa vitae."
                    />
                </Col>
            </Row>
            <Row className="home-article">
                <Col>
                    <Article
                        title="Local Cat Elected Mayor of Small Town"
                        img_src="/images/cat.jpg"
                        description="Foo bar baz qux quux corge grault garlpy waldo fred plugh xyzzy thud"
                    />
                </Col>
            </Row>
        </Container>
    );
};

export default Home;
