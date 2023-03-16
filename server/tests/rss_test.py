from tests import client, database_configure  # pyright: ignore
from flask import Flask


def test_add(client: Flask.testing) -> None:
    response = client.post("/rss/", json={"feeds": ["https://www.vrt.be/vrtnws/nl.rss.articles.xml"]})
    assert response.status_code == 200
