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
        data={"id1": article1.id, "id2": article2.id, "similarity": 0.9}
    )
    await db.similararticles.create(
        data={"id1": article2.id, "id2": article1.id, "similarity": 0.9}
    )

    await db.disconnect()

    def sync_part():
        response = client.get("/article/similar?", query_string={"url":"https://example.com/article1"}) 
        assert response.status_code == HTTPStatus.OK
        articles = response.get_json()["data"]["articles"]

        assert len(articles) == 1
        assert articles[0]["link"] == "https://example.com/article2"

        response = client.get("/article/similar?", query_string={"url":"https://example.com/article2"}) 
        assert response.status_code == HTTPStatus.OK
        articles = response.get_json()["data"]["articles"]

        assert len(articles) == 1
        assert articles[0]["link"] == "https://example.com/article1"
        
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, sync_part)