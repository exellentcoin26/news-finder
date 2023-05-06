from .utils import compare_json
from flask import Flask
from http import HTTPStatus


# Add feeds
def test_add_rss(client: Flask.testing):
    response = client.post(
        "/rss/",
        json={
            "feeds": [
                {
                    "name": "vrt-binnenland",
                    "feed": "https://www.vrt.be/vrtnws/nl.rss.articles_binnenland.xml",
                }
            ]
        },
    )
    assert response.status_code == HTTPStatus.OK

    response = client.get("/rss/")
    expected = """{
        "data": {
            "feeds": [
                {"source": "www.vrt.be", "feed": "https://www.vrt.be/vrtnws/nl.rss.articles_binnenland.xml"}
            ]
        },
        "errors": [],
        "status": 200
    }"""
    assert response.status_code == HTTPStatus.OK
    assert compare_json(expected, response.get_json())


def test_add_multiple_rss(client: Flask.testing):
    response = client.post(
        "/rss/",
        json={
            "feeds": [
                {
                    "name": "vrt-binnenland",
                    "feed": "https://www.vrt.be/vrtnws/nl.rss.articles_binnenland.xml",
                },
                {
                    "name": "vrt-buitenland",
                    "feed": "https://www.vrt.be/vrtnws/nl.rss.articles_buitenland.xml",
                },
                {
                    "name": "vrt-wetenschap",
                    "feed": "https://www.vrt.be/vrtnws/nl.rss.articles_wetenschap.xml",
                },
            ]
        },
    )
    assert response.status_code == HTTPStatus.OK

    response = client.get("/rss/")
    expected = """{
        "data": {
            "feeds": [
                {"source": "www.vrt.be", "feed": "https://www.vrt.be/vrtnws/nl.rss.articles_binnenland.xml"},
                {"source": "www.vrt.be", "feed": "https://www.vrt.be/vrtnws/nl.rss.articles_buitenland.xml"},
                {"source": "www.vrt.be", "feed": "https://www.vrt.be/vrtnws/nl.rss.articles_wetenschap.xml"}
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
                "message": "'feeds' is a required property"
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
            "feeds": [
                {
                    "name": "vrt-binnenland",
                    "feed": "https://www.vrt.be/vrtnws/nl.rss.articles_binnenland.xml",
                }
            ]
        },
    )
    response = client.post(
        "/rss/",
        json={
            "feeds": [
                {
                    "name": "vrt-binnenland",
                    "feed": "https://www.vrt.be/vrtnws/nl.rss.articles_binnenland.xml",
                }
            ]
        },
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST

    response = client.get("/rss/")
    expected = """{
        "data": {
            "feeds": [
                {"source": "www.vrt.be", "feed": "https://www.vrt.be/vrtnws/nl.rss.articles_binnenland.xml"}
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
            "feeds": [
                {
                    "name": "vrt-binnenland",
                    "feed": "https://www.vrt.be/vrtnws/nl.rss.articles_binnenland.xml",
                }
            ]
        },
    )
    assert response.status_code == HTTPStatus.OK

    response = client.get("/rss/")
    expected = """{
        "data": {
            "feeds": [
                {"source": "www.vrt.be", "feed": "https://www.vrt.be/vrtnws/nl.rss.articles_binnenland.xml"}
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
