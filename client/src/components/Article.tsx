import { Card, Row, Col, Container } from 'react-bootstrap';
import '../styles/Article.css';

const Article = ({
    title,
    img_src,
    description,
}: {
    title: string;
    img_src: string;
    description: string;
}) => {
    return (
        <Card className={'article-card'}>
            <Row md={1} className={'h-100'}>
                <Col className={'article-image'}>
                    <Card.Img
                        src={img_src}
                        className={'h-100'}
                        style={{ objectFit: 'cover' }}
                    />
                </Col>
                <Col className={'h-100 '}>
                    <Card.Body
                        className={'article-body'}
                        style={{
                            overflow: 'hidden',
                        }}
                    >
                        <Card.Title>{title}</Card.Title>
                        <Card.Text>{description}</Card.Text>
                    </Card.Body>
                </Col>
            </Row>
        </Card>
    );
};

export default Article;
