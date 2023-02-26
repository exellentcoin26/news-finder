#!/usr/bin/env python3

import asyncio

from flask import Flask

from routes.error import error_bp
from routes.user import user_bp
from routes.rss import rss_bp


async def main() -> None:
    app = Flask(__name__)

    # register subapplications/subroutes here
    app.register_blueprint(user_bp)
    app.register_blueprint(rss_bp)
    app.register_blueprint(error_bp)    # global error handling blueprint

    app.run()  # foo


if __name__ == '__main__':
    asyncio.run(main())
