from tests import client, database_configure, database_clear, compare_json  # pyright: ignore
from flask import Flask
from http import HTTPStatus


def test_add_rss(client: Flask.testing) -> None:
    response = client.post("/rss/", json={"feeds": ["https://www.vrt.be/vrtnws/nl.rss.articles_binnenland.xml"]})
    assert response.status_code == HTTPStatus.OK

    response = client.get("/rss/")
    expected = """{
        "feeds": [
            {"source": "www.vrt.be", "feed": "https://www.vrt.be/vrtnws/nl.rss.articles_binnenland.xml"}
        ]
    }"""
    assert response.status_code == HTTPStatus.OK
    assert compare_json(expected, response.get_json())


def test_add_multiple_rss(client: Flask.testing) -> None:
    response = client.post("/rss/", json={"feeds": ["https://www.vrt.be/vrtnws/nl.rss.articles_binnenland.xml",
                                                    "https://www.vrt.be/vrtnws/nl.rss.articles_buitenland.xml",
                                                    "https://www.vrt.be/vrtnws/nl.rss.articles_wetenschap.xml"]})
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


def test_add_duplicate_rss(client: Flask.testing) -> None:
    response = client.post("/rss/", json={"feeds": ["https://www.vrt.be/vrtnws/nl.rss.articles_binnenland.xml",
                                                    "https://www.vrt.be/vrtnws/nl.rss.articles_binnenland.xml"]})
    assert response.status_code == HTTPStatus.BAD_REQUEST

    response = client.get("/rss/")
    expected = """{
        "feeds": []
    }"""
    assert response.status_code == HTTPStatus.OK
    assert compare_json(expected, response.get_json())
