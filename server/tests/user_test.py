from tests import client, database_configure, database_clear, compare_json  # pyright: ignore
from flask import Flask
from http import HTTPStatus


# Register
def test_register_user(client: Flask.testing):
    response = client.post("/user/", json={"username": "john_doe", "password": "qwerty"})
    assert response.status_code == HTTPStatus.OK

    response = client.post("/user/", json={"username": "jane_doe", "password": "qwerty"})
    assert response.status_code == HTTPStatus.OK


def test_register_no_json(client: Flask.testing):
    response = client.post("/user/")
    expected = """{
        "error": "InvalidJson",
        "message": ""
    }"""
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert compare_json(expected, response.get_json())


def test_register_schema(client: Flask.testing):
    response = client.post("/user/", json={"username": "john_doe"})
    expected = """{
        "error": "JsonValidationError",
        "message": "'password' is a required property"
    }"""
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert compare_json(expected, response.get_json())

    response = client.post("/user/", json={"password": "qwerty"})
    expected = """{
        "error": "JsonValidationError",
        "message": "'username' is a required property"
    }"""
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert compare_json(expected, response.get_json())


def test_register_existing_username(client: Flask.testing):
    response = client.post("/user/", json={"username": "john_doe", "password": "qwerty"})
    response = client.post("/user/", json={"username": "john_doe", "password": "qwerty1"})
    expected = """{
        "error": "UserAlreadyPresent",
        "message": "User already present in database"
    }"""
    assert response.status_code == HTTPStatus.CONFLICT
    assert compare_json(expected, response.get_json())


def test_delete(client: Flask.testing):
    response = client.post("/user/", json={"username": "john_doe", "password": "qwerty"})
    assert response.status_code == HTTPStatus.OK

    response = client.delete("/user/", json={"username": "john_doe"})
    assert response.status_code == HTTPStatus.OK

    response = client.post("/user/login/", json={"username": "john_doe", "password": "qwerty"})
    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_delete_no_json(client: Flask.testing):
    response = client.delete("/user/")
    expected = """{
        "error": "InvalidJson",
        "message": ""
    }"""
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert compare_json(expected, response.get_json())


def test_delete_schema(client: Flask.testing):
    response = client.delete("/user/", json={"test": "test"})
    expected = """{
        "error": "JsonValidationError",
        "message": "'username' is a required property"
    }"""
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert compare_json(expected, response.get_json())


def test_delete_non_existing_user(client: Flask.testing):
    response = client.delete("/user/", json={"username": "john_doe"})
    assert response.status_code == HTTPStatus.BAD_REQUEST


# Login
def test_login(client: Flask.testing):
    response = client.post("/user/", json={"username": "john_doe", "password": "qwerty"})
    assert response.status_code == HTTPStatus.OK

    response = client.post("/user/login/", json={"username": "john_doe", "password": "qwerty"})
    assert response.status_code == HTTPStatus.OK


def test_login_casing(client: Flask.testing):
    response = client.post("/user/", json={"username": "JoHn_dOe", "password": "qwerty"})
    assert response.status_code == HTTPStatus.OK

    response = client.post("/user/login/", json={"username": "john_doe", "password": "qwerty"})
    assert response.status_code == HTTPStatus.OK


def test_login_no_json(client: Flask.testing):
    response = client.post("/user/login/")
    expected = """{
        "error": "InvalidJson",
        "message": ""
    }"""
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert compare_json(expected, response.get_json())


def test_login_user_schema(client: Flask.testing):
    response: Flask.response_class = client.post("/user/login/", json={"username": "abcd"})
    expected = """{
        "error": "JsonValidationError",
        "message": "'password' is a required property"
    }"""
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert compare_json(expected, response.get_json())

    response = client.post("/user/login/", json={"password": "abcd"})
    expected = """{
        "error": "JsonValidationError",
        "message": "'username' is a required property"
    }"""
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert compare_json(expected, response.get_json())


def test_login_non_existing_user(client: Flask.testing):
    response = client.post("/user/login/", json={"username": "jan", "password": "qwerty"})
    expected = """{
        "error": "RecordNotFoundError",
        "message": ""
    }"""
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert compare_json(expected, response.get_json())


def test_login_wrong_password(client: Flask.testing):
    response = client.post("/user/", json={"username": "john_doe", "password": "qwerty"})
    assert response.status_code == HTTPStatus.OK

    response = client.post("/user/login/", json={"username": "john_doe", "password": "qwerty1"})
    expected = """{
        "error": "WrongPassword",
        "message": ""
    }"""
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert compare_json(expected, response.get_json())


# Logout
def test_logout(client: Flask.testing):
    response = client.post("/user/", json={"username": "john_doe", "password": "qwerty"})
    assert response.status_code == HTTPStatus.OK

    response = client.post("/user/logout/")
    assert response.status_code == HTTPStatus.OK


def test_logout_not_logged_in(client: Flask.testing):
    response = client.post("/user/logout/")
    expected = """{
        "error": "CookieNotSet",
        "message": "Cookie not present in request"
    }"""
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert compare_json(expected, response.get_json())


# Status
def test_status(client: Flask.testing):
    response = client.post("/user/", json={"username": "john_doe", "password": "qwerty"})
    assert response.status_code == HTTPStatus.OK

    response = client.post("/user/status/")
    assert response.status_code == HTTPStatus.OK
    assert response.get_json()["logged_in"]


def test_status_no_cookie(client: Flask.testing):
    response = client.post("/user/status/")
    assert response.status_code == HTTPStatus.OK
    assert not response.get_json()["logged_in"]
