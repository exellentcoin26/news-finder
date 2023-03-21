from flask import Flask

from news_finder.routes.root import root_bp
from news_finder.routes.error import error_bp
from news_finder.routes.user import user_bp
from news_finder.routes.rss import rss_bp


def get_app() -> Flask:
    app = Flask(__name__)

    # register subapplications/subroutes here
    app.register_blueprint(user_bp)
    app.register_blueprint(rss_bp)
    app.register_blueprint(root_bp)
    app.register_blueprint(error_bp)  # global error handling blueprint

    return app
