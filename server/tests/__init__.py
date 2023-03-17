import pytest
from os import environ
import pytest_asyncio
from prisma import Prisma
from flask import Flask
from news_finder.routes.root import root_bp
from news_finder.routes.error import error_bp
from news_finder.routes.user import user_bp
from news_finder.routes.rss import rss_bp

app = Flask(__name__)
app.register_blueprint(user_bp)
app.register_blueprint(rss_bp)
app.register_blueprint(root_bp)
app.register_blueprint(error_bp)


@pytest.fixture
def client() -> Flask.testing:
    return app.test_client()


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
