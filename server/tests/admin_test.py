from .utils import compare_json
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
    assert response.get_json()["data"]["admin"]


def test_add_admin_no_json(client: Flask.testing):
    response = client.post("/admin/")
    expected = """{
        "data": {},
        "errors": [
            {
                "kind": "InvalidJson",
                "message": ""
            }
        ],
        "status": 400
    }"""
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert compare_json(expected, response.get_json())


def test_add_admin_schema(client: Flask.testing):
    response = client.post("/admin/", json={"test": "test"})
    expected = """{
        "data": {},
        "errors": [
            {
                "kind": "JsonValidationError",
                "message": "'usernames' is a required property"
            }
        ],
        "status": 400
    }"""
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert compare_json(expected, response.get_json())

    response = client.post("/admin/", json={"usernames": "Jan"})
    expected = """{
        "data": {},
        "errors": [
            {
                "kind": "JsonValidationError",
                "message": "'Jan' is not of type 'array'"
            }
        ],
        "status": 400
    }"""
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert compare_json(expected, response.get_json())


# Is admin
def test_add_admin_non_existing_user(client: Flask.testing):
    response = client.post("/admin/", json={"usernames": ["Jan"]})
    expected = """{
        "data": {},
        "errors": [
            {
                "kind": "RecordNotFoundError",
                "message": "An operation failed because it depends on one or more records that were required but not found. Record to update not found."
            }
        ],
        "status": 400
    }"""
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert compare_json(expected, response.get_json())


# Status
def test_status(client: Flask.testing):
    response = client.post("/user/", json={"username": "jan", "password": "qwerty"})
    assert response.status_code == HTTPStatus.OK
    response = client.post(
        "/user/", json={"username": "piet-joris", "password": "qwerty"}
    )
    assert response.status_code == HTTPStatus.OK

    response_make_admin = client.post("/admin/", json={"usernames": ["jan"]})
    assert response_make_admin.status_code == HTTPStatus.OK

    response = client.post("/admin/", json={"usernames": ["Jan", "piet-joris"]})
    assert response.status_code == HTTPStatus.OK


def test_status_no_json(client: Flask.testing):
    response = client.post("/admin/")
    expected = """{
        "data": {},
        "errors": [
            {
                "kind": "InvalidJson",
                "message": ""
            }
        ],
        "status": 400
    }"""
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert compare_json(expected, response.get_json())


def test_status_schema(client: Flask.testing):
    response = client.post("/admin/", json={"test": "test"})
    expected = """{
        "data": {},
        "errors": [
            {
                "kind": "JsonValidationError",
                "message": "'usernames' is a required property"
            }
        ],
        "status": 400
    }"""
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert compare_json(expected, response.get_json())
