import pytest
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
def client() -> Flask.test_client:
    return app.test_client()
