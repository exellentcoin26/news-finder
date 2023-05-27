import asyncio
from datetime import datetime, timedelta

from flask import Flask
from http import HTTPStatus
from prisma import Prisma


async def test_get_articles_with_updated_version(client: Flask.testing):
    db = Prisma()
    await db.connect()

    source = await db.newssources.create(
        data={"url": "https://test.com", "name": "test.com"}
    )

    article1 = await db.newsarticles.create(
        data={
            "source": {"connect": {"id": source.id}},
            "url": "https://example.com/article1",
            "title": "Article 1",
            "publication_date": datetime.now() - timedelta(hours=4),
        }
    )
    article2 = await db.newsarticles.create(
        data={
            "source": {"connect": {"id": source.id}},
            "url": "https://example.com/article2",
            "title": "Article 2",
            "publication_date": datetime.now(),
        }
    )

    await db.similararticles.create(
        data={"id1": article1.id, "id2": article2.id, "similarity": 0.9}
    )
    await db.similararticles.create(
        data={"id1": article2.id, "id2": article1.id, "similarity": 0.9}
    )

    await db.disconnect()

    def sync_part():
        response = client.get("/article/")
        assert response.status_code == HTTPStatus.OK
        articles = response.get_json()["data"]["articles"]

        assert len(articles) == 1
        assert articles[0]["article"]["title"] == "Article 2"

    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, sync_part)


async def test_get_sort_by_popularity(client: Flask.testing):
    db = Prisma()
    await db.connect()

    source1 = await db.newssources.create(
        data={"url": "https://test.com", "name": "test.com"}
    )
    source2 = await db.newssources.create(
        data={"url": "https://example.com", "name": "example.com"}
    )
    source3 = await db.newssources.create(
        data={"url": "https://noclue.com", "name": "noclue.com"}
    )

    await db.newsarticles.create(
        data={
            "source": {"connect": {"id": source1.id}},
            "url": "https://test.com/article1",
            "title": "Article 1",
            "publication_date": datetime.now(),
        }
    )
    await db.newsarticles.create(
        data={
            "source": {"connect": {"id": source2.id}},
            "url": "https://example.com/article2",
            "title": "Article 2",
            "publication_date": datetime.now(),
        }
    )
    await db.newsarticles.create(
        data={
            "source": {"connect": {"id": source3.id}},
            "url": "https://noclue.com/article3",
            "title": "Article 3",
            "publication_date": datetime.now(),
        }
    )

    def sync_part():
        # Create users
        response = client.post(
            "/user/", json={"username": "john_doe", "password": "qwerty"}
        )
        assert response.status_code == HTTPStatus.OK
        response = client.post(
            "/user/", json={"username": "jane_doe", "password": "qwerty"}
        )
        assert response.status_code == HTTPStatus.OK
        response = client.post(
            "/user/", json={"username": "bart_doe", "password": "qwerty"}
        )
        assert response.status_code == HTTPStatus.OK

        # Click on articles
        # Login as user 1
        response = client.post(
            "/user/login/", json={"username": "john_doe", "password": "qwerty"}
        )
        assert response.status_code == HTTPStatus.OK
        response = client.post(
            "/user-history/", json={"articleLink": "https://example.com/article2"}
        )
        assert response.status_code == HTTPStatus.OK
        # Login as user 2
        response = client.post(
            "/user/login/", json={"username": "jane_doe", "password": "qwerty"}
        )
        response = client.post(
            "/user-history/", json={"articleLink": "https://test.com/article1"}
        )
        assert response.status_code == HTTPStatus.OK
        response = client.post(
            "/user-history/", json={"articleLink": "https://example.com/article2"}
        )
        assert response.status_code == HTTPStatus.OK

        response = client.get("/article/?sortBy=popularity")
        assert response.status_code == HTTPStatus.OK
        articles = response.get_json()["data"]["articles"]
        assert len(articles) == 2
        assert articles[0]["article"]["title"] == "Article 2"
        assert articles[1]["article"]["title"] == "Article 1"

    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, sync_part)


async def test_get_similar_articles(client: Flask.testing):
    db = Prisma()
    await db.connect()

    source = await db.newssources.create(
        data={"url": "https://test.com", "name": "test.com"}
    )

    article1 = await db.newsarticles.create(
        data={
            "source": {"connect": {"id": source.id}},
            "url": "https://example.com/article1",
            "title": "Article 1",
            "publication_date": datetime.now() - timedelta(hours=4),
        }
    )
    article2 = await db.newsarticles.create(
        data={
            "source": {"connect": {"id": source.id}},
            "url": "https://example.com/article2",
            "title": "Article 2",
            "publication_date": datetime.now(),
        }
    )

    await db.similararticles.create(
        data={
            "id1": article1.id,
            "id2": article2.id,
            "similarity": 0.9,
        }
    )

    await db.similararticles.create(
        data={
            "id1": article2.id,
            "id2": article1.id,
            "similarity": 0.9,
        }
    )

    await db.disconnect()

    def sync_part():
        response = client.get(
            "/article/similar/?", query_string={"url": "https://example.com/article1"}
        )
        assert response.status_code == HTTPStatus.OK
        articles = response.get_json()["data"]["articles"]

        assert len(articles) == 1
        assert articles[0]["link"] == "https://example.com/article2"

        response = client.get(
            "/article/similar/?", query_string={"url": "https://example.com/article2"}
        )
        assert response.status_code == HTTPStatus.OK
        articles = response.get_json()["data"]["articles"]

        assert len(articles) == 1
        assert articles[0]["link"] == "https://example.com/article1"

    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, sync_part)
