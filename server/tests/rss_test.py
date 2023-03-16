from tests import *  # pyright: ignore


def test_add(client: Flask.testing) -> None:
    response = client.post("/rss/", json={"feeds": ["https://www.vrt.be/vrtnws/nl.rss.articles.xml"]})
    assert response.status_code == 200
