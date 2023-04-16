import Container from 'react-bootstrap/Container';
import Col from 'react-bootstrap/Col';
import Row from 'react-bootstrap/Row';
const About = () => {
    return (
        <Container>
            <Row>
                <Col>
                    <h1>Our Mission</h1>
                    <p>
                        Our news aggregator collects and displays news articles
                        from a variety of news sources, providing users with a
                        centralized website to stay up-to-date with current
                        events. To improve our users experience, we have
                        intergrated an algorithm to recommend articles based on
                        their previous activity.
                    </p>
                </Col>
            </Row>
            <Row>
                <Col md={12}>
                    <h2>Meet the Team</h2>
                </Col>
                <Col>
                    <p>Jonas Caluwé (2nd Bachelor Computer Science)</p>
                    <p>David Scalais (2nd Bachelor Computer Science)</p>
                    <p>Laurens De Wachter (2nd Bachelor Computer Science)</p>
                    <p>Chloe Mansibang (2nd Bachelor Computer Science)</p>
                    <p>Ayoub El Marchouchi (2nd Bachelor Computer Science)</p>
                </Col>
            </Row>
            <Row>
                <Col md={12}>
                    <h2>Functionality</h2>
                    <ul>
                        <li>
                            News articles are pulled from a variety of sources
                            and displayed in a single location
                        </li>
                        <li>Users can filter articles by category</li>
                        <li>
                            Article summaries and images are displayed for easy
                            browsing
                        </li>
                        <li>
                            Users can click on individual articles to read the
                            full story on the source website
                        </li>
                        <li>
                            Articles are updated in real-time as new content
                            becomes available
                        </li>
                        <li>
                            Users gets articles recommended by a recommendation
                            system
                        </li>
                        <li>
                            For a better view similar articles are also group
                            together
                        </li>
                    </ul>
                </Col>
            </Row>
        </Container>
    );
};

export default About;
