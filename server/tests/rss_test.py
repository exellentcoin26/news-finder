from tests import (
    client,
    database_configure,
    database_clear,
    compare_json,
)  # pyright: ignore
from flask import Flask
from http import HTTPStatus


# Add feeds
def test_add_rss(client: Flask.testing):
    response = client.post(
        "/rss/",
        json={"feeds": ["https://www.vrt.be/vrtnws/nl.rss.articles_binnenland.xml"]},
    )
    assert response.status_code == HTTPStatus.OK

    response = client.get("/rss/")
    expected = """{
        "feeds": [
            {"source": "www.vrt.be", "feed": "https://www.vrt.be/vrtnws/nl.rss.articles_binnenland.xml"}
        ]
    }"""
    assert response.status_code == HTTPStatus.OK
    assert compare_json(expected, response.get_json())


def test_add_multiple_rss(client: Flask.testing):
    response = client.post(
        "/rss/",
        json={
            "feeds": [
                "https://www.vrt.be/vrtnws/nl.rss.articles_binnenland.xml",
                "https://www.vrt.be/vrtnws/nl.rss.articles_buitenland.xml",
                "https://www.vrt.be/vrtnws/nl.rss.articles_wetenschap.xml",
            ]
        },
    )
    assert response.status_code == HTTPStatus.OK

    response = client.get("/rss/")
    expected = """{
        "feeds": [
            {"source": "www.vrt.be", "feed": "https://www.vrt.be/vrtnws/nl.rss.articles_binnenland.xml"},
            {"source": "www.vrt.be", "feed": "https://www.vrt.be/vrtnws/nl.rss.articles_buitenland.xml"},
            {"source": "www.vrt.be", "feed": "https://www.vrt.be/vrtnws/nl.rss.articles_wetenschap.xml"}
        ]
    }"""
    assert response.status_code == HTTPStatus.OK
    assert compare_json(expected, response.get_json())


def test_add_rss_no_json(client: Flask.testing):
    response = client.post("/rss/")
    expected = """{
        "error": "InvalidJson",
        "message": ""
    }"""
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert compare_json(expected, response.get_json())


def test_add_rss_schema(client: Flask.testing):
    response = client.post("/rss/", json={"test": "test"})
    expected = """{
        "error": "JsonValidationError",
        "message": "'feeds' is a required property"
    }"""
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert compare_json(expected, response.get_json())


def test_add_duplicate_rss(client: Flask.testing):
    response = client.post(
        "/rss/",
        json={
            "feeds": [
                "https://www.vrt.be/vrtnws/nl.rss.articles_binnenland.xml",
                "https://www.vrt.be/vrtnws/nl.rss.articles_binnenland.xml",
            ]
        },
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST

    response = client.get("/rss/")
    expected = """{
        "feeds": []
    }"""
    assert response.status_code == HTTPStatus.OK
    assert compare_json(expected, response.get_json())


# Delete feeds
def test_delete_rss(client: Flask.testing):
    response = client.post(
        "/rss/",
        json={"feeds": ["https://www.vrt.be/vrtnws/nl.rss.articles_binnenland.xml"]},
    )
    assert response.status_code == HTTPStatus.OK

    response = client.get("/rss/")
    expected = """{
        "feeds": [
            {"source": "www.vrt.be", "feed": "https://www.vrt.be/vrtnws/nl.rss.articles_binnenland.xml"}
        ]
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
        "feeds": []
    }"""
    assert response.status_code == HTTPStatus.OK
    assert compare_json(expected, response.get_json())


def test_delete_rss_no_json(client: Flask.testing):
    response = client.delete("/rss/")
    expected = """{
        "error": "InvalidJson",
        "message": ""
    }"""
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert compare_json(expected, response.get_json())


def test_delete_rss_schema(client: Flask.testing):
    response = client.delete("/rss/", json={"test": "test"})
    expected = """{
        "error": "JsonValidationError",
        "message": "'feeds' is a required property"
    }"""
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert compare_json(expected, response.get_json())


def test_delete_rss_not_found(client: Flask.testing):
    response = client.delete(
        "/rss/",
        json={"feeds": ["https://www.vrt.be/vrtnws/nl.rss.articles_binnenland.xml"]},
    )
    expected = """{
        "error": "RecordNotFoundError",
        "message": "An operation failed because it depends on one or more records that were required but not found. Record to delete does not exist."
    }"""
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert compare_json(expected, response.get_json())
