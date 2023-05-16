import { useEffect, useState } from 'react';
import { LabelsApiResponse } from '../interfaces/api/labels';
import { Col, Container, Row } from 'react-bootstrap';
import { Label } from './Label';

import '../styles/LabelBar.css';

const getLabelsFromServer = async (): Promise<string[]> => {
    const serverUrl =
        import.meta.env['VITE_SERVER_URL'] || 'http://localhost:5000';

    const response = await (async (): Promise<Response> => {
        try {
            return await fetch(serverUrl + '/labels/');
        } catch (e) {
            console.error(e);
            throw e;
        }
    })();

    const body = await response.text();

    const labelsApiResponse = ((): LabelsApiResponse => {
        try {
            return JSON.parse(body);
        } catch (e) {
            console.debug(body);
            throw e;
        }
    })();

    if (labelsApiResponse.data == null) {
        throw new Error('data property on `ArticleApiResponse` is not set');
    }

    return labelsApiResponse.data.labels;
};

export const LabelBar = ({ onClick }: { onClick: (name: string) => void }) => {
    const [labels, setLabels] = useState<string[]>([]);
    const [isLoading, setIsLoading] = useState<boolean>(true);

    useEffect(() => {
        const fetchLabels = async () => {
            try {
                const labels = await getLabelsFromServer();
                setLabels(labels);
            } catch (error) {
                console.error(error);
            } finally {
                setIsLoading(false);
            }
        };

        fetchLabels();
    }, []);

    return (
        <Container>
            {isLoading ? (
                <Container>No categories found</Container>
            ) : (
                <Row className="flex-nowrap overflow-auto hide-scroll">
                    {labels.map((label, index) => {
                        return (
                            <Col key={index}>
                                <Label name={label} onClick={onClick} />
                            </Col>
                        );
                    })}
                </Row>
            )}
        </Container>
    );
};
export default LabelBar;
