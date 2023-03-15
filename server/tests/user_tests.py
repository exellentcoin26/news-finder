from tests import *


def test_hello_user(client) -> None:
    response = client.get("/user/")
    assert response.status_code == 200
    assert response.data == b"Hello, User!"
