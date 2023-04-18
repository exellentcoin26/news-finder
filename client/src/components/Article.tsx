import { Card, Row, Col } from 'react-bootstrap';
import '../styles/Article.css';

export const Article = ({
    title,
    img_src,
    description,
    article_link,
}: {
    title: string;
    img_src?: string;
    description?: string;
    article_link: string;
}) => {
    return (
        <a
            href={article_link}
            style={{ textDecoration: 'none', color: 'inherit' }}
        >
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
        </a>
    );
};

export const ArticlePlaceholder = () => {
    return <h1>No articles loaded yet... Loading!</h1>;
};

export const NoArticlesToShow = () => {
    return <h1>No articles in database.</h1>;
};
