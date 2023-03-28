from tests import client, database_configure, database_clear  # pyright: ignore
from flask import Flask
from http import HTTPStatus
from jsoncomparison import Compare, NO_DIFF  # pyright: ignore   TODO: Check with Jonas


def test_add_rss(client: Flask.testing) -> None:
    response = client.post("/rss/", json={"feeds": ["https://www.vrt.be/vrtnws/nl.rss.articles_binnenland.xml"]})
    assert response.status_code == HTTPStatus.OK

    response = client.get("/rss/")
    assert response.status_code == HTTPStatus.OK
    assert response.get_json() == {
        "feeds": [{"source": "www.vrt.be", "feed": "https://www.vrt.be/vrtnws/nl.rss.articles_binnenland.xml"}]}


def test_add_multiple_rss(client: Flask.testing) -> None:
    response = client.post("/rss/", json={"feeds": ["https://www.vrt.be/vrtnws/nl.rss.articles_binnenland.xml",
                                                    "https://www.vrt.be/vrtnws/nl.rss.articles_buitenland.xml",
                                                    "https://www.vrt.be/vrtnws/nl.rss.articles_wetenschap.xml"]})
    assert response.status_code == HTTPStatus.OK

    response = client.get("/rss/")
    expected: dict[str, list[dict[str, str]]] = {
        "feeds": [{"source": "www.vrt.be", "feed": "https://www.vrt.be/vrtnws/nl.rss.articles_binnenland.xml"},
                  {"source": "www.vrt.be", "feed": "https://www.vrt.be/vrtnws/nl.rss.articles_buitenland.xml"},
                  {"source": "www.vrt.be", "feed": "https://www.vrt.be/vrtnws/nl.rss.articles_wetenschap.xml"}]
    }
    assert response.status_code == HTTPStatus.OK
    assert Compare().check(expected, response.get_json()) == NO_DIFF  # pyright: ignore  TODO: Check with Jonas


def test_add_duplicate_rss(client: Flask.testing) -> None:
    response = client.post("/rss/", json={"feeds": ["https://www.vrt.be/vrtnws/nl.rss.articles_binnenland.xml",
                                                    "https://www.vrt.be/vrtnws/nl.rss.articles_binnenland.xml"]})
    assert response.status_code == HTTPStatus.BAD_REQUEST

    response = client.get("/rss/")
    expected: dict[str, list[dict[str, str]]] = {
        "feeds": []
    }
    assert response.status_code == HTTPStatus.OK
    assert Compare().check(expected, response.get_json()) == NO_DIFF  # pyright: ignore  TODO: Check with Jonas
