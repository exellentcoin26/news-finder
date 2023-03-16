import pytest
from os import environ
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
