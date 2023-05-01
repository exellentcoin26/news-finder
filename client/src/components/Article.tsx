import {Card, Row, Col, Popover, OverlayTrigger, ListGroup} from 'react-bootstrap';
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
                            src={img_src ? img_src : '/img/no-image.png'}
                            className={'h-100'}
                            style={
                                img_src
                                    ? { objectFit: 'cover' }
                                    : { objectFit: 'contain' }
                            }
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
                            <OverlayTrigger
                                placement="right"
                                trigger="click"
                                overlay={(<Popover>
                                        <ListGroup>
                                            <ListGroup.Item>Cras justo odio</ListGroup.Item>
                                            <ListGroup.Item>Dapibus ac facilisis in</ListGroup.Item>
                                            <ListGroup.Item>Morbi leo risus</ListGroup.Item>
                                            <ListGroup.Item>Porta ac consectetur ac</ListGroup.Item>
                                            <ListGroup.Item>Vestibulum at eros</ListGroup.Item>
                                        </ListGroup>
                                    </Popover>
                                )}>
                                <button className="similar-articles-button"> show similar </button>
                            </OverlayTrigger>
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
