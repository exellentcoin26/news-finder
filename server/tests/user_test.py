from tests import *  # pyright: ignore


def test_hello_user(client: Flask.testing) -> None:
    response = client.get("/user/")
    assert response.status_code == 200
    assert response.data == b"Hello, User!"
