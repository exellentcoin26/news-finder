from .utils import compare_json
from flask import Flask
from http import HTTPStatus


# Add feeds
def test_add_rss_without_interval(client: Flask.testing):
    response = client.post(
        "/rss/",
        json={
            "name": "vrt-binnenland",
            "feed": "https://www.vrt.be/vrtnws/nl.rss.articles_binnenland.xml",
            "category": "binnenland",
        },
    )
    assert response.status_code == HTTPStatus.OK

    response = client.get("/rss/")
    expected = """{
        "data": {
            "feeds": [
                {
                    "source": "www.vrt.be",
                    "feed": "https://www.vrt.be/vrtnws/nl.rss.articles_binnenland.xml",
                    "name": "vrt-binnenland"
                }
            ]
        },
        "errors": [],
        "status": 200
    }"""
    assert response.status_code == HTTPStatus.OK
    assert compare_json(expected, response.get_json())


def test_add_rss_with_interval(client: Flask.testing):
    response = client.post(
        "/rss/",
        json={
            "name": "vrt-binnenland",
            "feed": "https://www.vrt.be/vrtnws/nl.rss.articles_binnenland.xml",
            "category": "binnenland",
            "interval": 4,
        },
    )
    assert response.status_code == HTTPStatus.OK

    response = client.get("/rss/")
    expected = """{
        "data": {
            "feeds": [
                {
                    "source": "www.vrt.be",
                    "feed": "https://www.vrt.be/vrtnws/nl.rss.articles_binnenland.xml",
                    "name": "vrt-binnenland"
                }
            ]
        },
        "errors": [],
        "status": 200
    }"""
    assert response.status_code == HTTPStatus.OK
    assert compare_json(expected, response.get_json())


def test_add_rss_no_json(client: Flask.testing):
    response = client.post("/rss/")
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


def test_add_rss_schema(client: Flask.testing):
    response = client.post("/rss/", json={"test": "test"})
    expected = """{
        "data": {},
        "errors": [
            {
                "kind": "JsonValidationError",
                "message": "'name' is a required property"
            }
        ],
        "status": 400
    }"""
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert compare_json(expected, response.get_json())


def test_add_duplicate_rss(client: Flask.testing):
    client.post(
        "/rss/",
        json={
            "name": "vrt-binnenland",
            "feed": "https://www.vrt.be/vrtnws/nl.rss.articles_binnenland.xml",
            "category": "binnenland",
        },
    )
    response = client.post(
        "/rss/",
        json={
            "name": "vrt-binnenland",
            "feed": "https://www.vrt.be/vrtnws/nl.rss.articles_binnenland.xml",
            "category": "binnenland",
        },
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST

    response = client.get("/rss/")
    expected = """{
        "data": {
            "feeds": [
                {
                    "source": "www.vrt.be",
                    "feed": "https://www.vrt.be/vrtnws/nl.rss.articles_binnenland.xml",
                    "name": "vrt-binnenland"
                }
            ]
        },
        "errors": [],
        "status": 200
    }"""
    assert response.status_code == HTTPStatus.OK
    assert compare_json(expected, response.get_json())


# Delete feeds
def test_delete_rss(client: Flask.testing):
    response = client.post(
        "/rss/",
        json={
            "name": "vrt-binnenland",
            "feed": "https://www.vrt.be/vrtnws/nl.rss.articles_binnenland.xml",
            "category": "binnenland",
        },
    )
    assert response.status_code == HTTPStatus.OK

    response = client.get("/rss/")
    expected = """{
        "data": {
            "feeds": [
                {
                    "source": "www.vrt.be",
                    "feed": "https://www.vrt.be/vrtnws/nl.rss.articles_binnenland.xml",
                    "name": "vrt-binnenland"
                }
            ]
        },
        "errors": [],
        "status": 200
    }"""
    assert response.status_code == HTTPStatus.OK
    assert compare_json(expected, response.get_json())

    response = client.delete(
        "/rss/",
        json={"feeds": ["https://www.vrt.be/vrtnws/nl.rss.articles_binnenland.xml"]},
    )
    assert response.status_code == HTTPStatus.OK

    response = client.get("/rss/")
    expected = """{
        "data": {
            "feeds": []
        },
        "errors": [],
        "status": 200
    }"""
    assert response.status_code == HTTPStatus.OK
    assert compare_json(expected, response.get_json())


def test_delete_rss_no_json(client: Flask.testing):
    response = client.delete("/rss/")
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


def test_delete_rss_schema(client: Flask.testing):
    response = client.delete("/rss/", json={"test": "test"})
    expected = """{
        "data": {},
        "errors": [
            {
                "kind": "JsonValidationError",
                "message": "'feeds' is a required property"
            }
        ],
        "status": 400
    }"""
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert compare_json(expected, response.get_json())


def test_delete_rss_not_found(client: Flask.testing):
    response = client.delete(
        "/rss/",
        json={"feeds": ["https://www.vrt.be/vrtnws/nl.rss.articles_binnenland.xml"]},
    )
    expected = """{
            "data": {},
            "errors": [
                {
                    "kind": "RecordNotFoundError",
                    "message": ""
                }
            ],
            "status": 400
    }"""
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert compare_json(expected, response.get_json())
