#!/usr/bin/env python3

from flask import Flask

from routes.error import error_bp
from routes.user import user_bp


if __name__ == '__main__':
    app = Flask(__name__)

    # register subapplications/subroutes here
    app.register_blueprint(user_bp)
    app.register_blueprint(error_bp)    # global error handling blueprint

    app.run()
