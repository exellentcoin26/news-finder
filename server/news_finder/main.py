#!/usr/bin/env python3

import path_setup  # pyright: ignore # noqa

import asyncio

from flask import Flask

from news_finder.routes.root import root_bp
from news_finder.routes.error import error_bp
from news_finder.routes.user import user_bp
from news_finder.routes.rss import rss_bp
from news_finder.routes.delete_rss import delete_rss_bp


async def main():
    app = Flask(__name__)

    # register subapplications/subroutes here
    app.register_blueprint(user_bp)
    app.register_blueprint(rss_bp)
    app.register_blueprint(root_bp)
    app.register_blueprint(error_bp)  # global error handling blueprint
    app.register_blueprint(delete_rss_bp)

    try:
        app.run(debug=True, host="0.0.0.0")
    except Exception as e:
        print(e.with_traceback(None))


if __name__ == "__main__":
    asyncio.run(main(), debug=True)
