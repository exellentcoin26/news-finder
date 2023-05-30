import { Button } from 'react-bootstrap';
import '../styles/LabelBar.css'

export const Label = ({
    name,
    onClick,
}: {
    name: string;
    onClick: (name: string) => void;
}) => {
    const handleButtonClick = (label: string) => {
        onClick(label);
    };

    return (
        <Button className="label" onClick={() => handleButtonClick(name)}>
            {name}
        </Button>
    );
};

export default Label;