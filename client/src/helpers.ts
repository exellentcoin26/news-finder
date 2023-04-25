import { AdminStatusApiResponse } from './interfaces/api/admin';

import { SERVER_URL } from './env';

export const fetchAdminStatus = async (
    setIsAdmin: (isAdmin: boolean) => void,
    setIsFetchingAdmin: (isAdmin: boolean) => void,
) => {
    const response = await fetch(SERVER_URL + '/admin/', {
        method: 'GET',
        credentials: 'include',
    });

    const adminStatusApiResponse: AdminStatusApiResponse =
        await response.json();

    if (adminStatusApiResponse.data == null) {
        throw new Error('data property on `AdminStatusApiResponse` object');
    }

    if (adminStatusApiResponse.data.admin) {
        setIsAdmin(true);
    } else {
        setIsAdmin(false);
    }
    setIsFetchingAdmin(false);
};
