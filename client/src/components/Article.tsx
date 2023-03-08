import Container from 'react-bootstrap/Container';
import Image from 'react-bootstrap/Image';
import React from 'react';
import '../styles/Article.css';
import { Link } from 'react-router-dom';

const Article: React.FC<{ title: string; img_src: string; alt: string }> = ({
    title,
    img_src,
    alt,
}) => {
    return (
        <Container className="article-container p-0">
            <Link to="/" className="article-link">
                <Container className="image-container p-0">
                    <Image
                        src={img_src}
                        alt={alt}
                        className="article-img img-fluid justify-content-center"
                    />
                </Container>
                <Container className="text-container py-1 px-2">
                    {title}
                </Container>
            </Link>
        </Container>
    );
};

export default Article;
