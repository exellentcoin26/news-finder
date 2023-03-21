from tests import client, database_configure, database_clear  # pyright: ignore
from flask import Flask


def test_hello_user(client: Flask.testing) -> None:
    response = client.get("/user/")
    assert response.status_code == 200
    assert response.data == b"Hello, User!"


def test_register_new_user(client: Flask.testing) -> None:
    response: Flask.response_class = client.post("/user/", json={"username": "abcd", "password": "dcba"})
    assert response.status_code == 200


def test_unique_username(client: Flask.testing) -> None:
    response: Flask.response_class = client.post("/user/", json={"username": "abcd", "password": "dcba"})
    response: Flask.response_class = client.post("/user/", json={"username": "abcd", "password": "dcba1"})
    assert response.status_code == 409

def test_log_out(client: Flask.testing) -> None:
    pass