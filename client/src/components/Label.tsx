import { Button } from 'react-bootstrap';

export const Label = ({ name }: { name: string }) => {
    return <Button className="label">{name}</Button>;
};

export default Label;
