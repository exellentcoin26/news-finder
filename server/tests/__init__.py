import pytest
import pytest_asyncio
from os import environ
from prisma import Prisma
from flask import Flask
from news_finder.app import get_app


@pytest.fixture
def client() -> Flask.testing:
    return get_app().test_client()


@pytest.fixture(scope="session", autouse=True)
def database_configure():
    environ["DATABASE_URL"] = "postgres://ppdb_admin:admin@localhost:5432/ppdb_test"


@pytest_asyncio.fixture(scope="function", autouse=True)  # pyright: ignore
async def database_clear():
    db = Prisma()
    await db.connect()

    async with db.batch_() as b:
        b.users.delete_many()
        b.userlogins.delete_many()
        b.usercookies.delete_many()
        b.newssources.delete_many()
        b.rssentries.delete_many()
        b.newsarticles.delete_many()
        b.similararticles.delete_many()
        b.labels.delete_many()
        b.newsarticlelabels.delete_many()

    await b.commit()

    await db.disconnect()
