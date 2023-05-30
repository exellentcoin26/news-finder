from flask import Flask
from flask_cors import CORS

from news_finder.routes.root import root_bp
from news_finder.routes.admin import admin_bp
from news_finder.routes.error import error_bp
from news_finder.routes.user import user_bp
from news_finder.routes.rss import rss_bp
from news_finder.routes.article import article_bp
from news_finder.routes.source import source_bp
from news_finder.routes.labels import labels_bp
from news_finder.routes.user_history import history_bp


def get_app() -> Flask:
    app = Flask(__name__)
    CORS(app)

    # register subapplications/subroutes here
    app.register_blueprint(user_bp)
    app.register_blueprint(rss_bp)
    app.register_blueprint(article_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(root_bp)
    app.register_blueprint(source_bp)
    app.register_blueprint(labels_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(error_bp)  # global error handling blueprint

    return app
