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


def test_login(client: Flask.testing) -> None:
    response_create_user: Flask.response_class = client.post("/user/", json={"username": "jan", "password": "qwerty"})
    assert response_create_user.status_code == 200

    response_login: Flask.response_class = client.post("/user/login/", json={"username": "jan", "password": "qwerty",
                                                                             "cookie": "ksdaflsakdjfhdsalkfjh"})
    assert response_login.status_code == 200


def test_wrong_login(client: Flask.testing) -> None:
    response_login: Flask.response_class = client.post("/user/login/", json={"username": "jan", "password": "qwerty",
                                                                             "cookie": "ksdaflsakdjfhdsalkfjh"})
    assert response_login.status_code == 400
