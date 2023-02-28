from flask import Blueprint, Response

user_bp = Blueprint("user", __name__, url_prefix="/user")


@user_bp.get("/")
def hello_user() -> Response:
    return Response("Hello, User!")
