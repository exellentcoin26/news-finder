from tests import client, database_configure, database_clear, compare_json  # pyright: ignore
from flask import Flask
from http import HTTPStatus


# Add admin
def test_add_admin(client: Flask.testing):
    response = client.post("/user/", json={"username": "jan", "password": "qwerty"})
    assert response.status_code == HTTPStatus.OK

    response_make_admin = client.post("/admin/", json={"usernames": ["Jan"]})
    assert response_make_admin.status_code == HTTPStatus.OK

    response = client.get("/admin/")
    assert response.status_code == HTTPStatus.OK
    assert response.get_json()["admin"]


def test_add_admin_no_json(client: Flask.testing):
    response = client.post("/admin/")
    expected = """{
        "error": "InvalidJson",
        "message": ""
    }"""
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert compare_json(expected, response.get_json())


def test_add_admin_schema(client: Flask.testing):
    response = client.post("/admin/", json={"test": "test"})
    expected = """{
        "error": "JsonValidationError",
        "message": "'usernames' is a required property"
    }"""
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert compare_json(expected, response.get_json())

    response = client.post("/admin/", json={"usernames": "Jan"})
    expected = """{
        "error": "JsonValidationError",
        "message": "'Jan' is not of type 'array'"
    }"""
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert compare_json(expected, response.get_json())


# Is admin
def test_add_admin_non_existing_user(client: Flask.testing):
    response = client.post("/admin/", json={"usernames": ["Jan"]})
    expected = """{
        "error": "RecordNotFoundError",
        "message": "An operation failed because it depends on one or more records that were required but not found. Record to update not found."
    }"""
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert compare_json(expected, response.get_json())
