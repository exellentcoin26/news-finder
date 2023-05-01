import { Container } from 'react-bootstrap';

export const Label = ({ name }: { name: string }) => {
    return <Container className="label">{name}</Container>;
};

export default Label;
