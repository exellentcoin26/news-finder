from tests import client, database_configure, database_clear  # pyright: ignore
from flask import Flask


def test_hello_user(client: Flask.testing) -> None:
    response = client.get("/user/")
    assert response.status_code == 200
    assert response.data == b"Hello, User!"