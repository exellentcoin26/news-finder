from flask import Blueprint, Response, request
from flask_cors import CORS
from http import HTTPStatus
from jsonschema import SchemaError, validate, ValidationError
import sys
from typing import List

from news_finder.db import get_db
from news_finder.response import (
    make_response_from_error,
    ErrorKind,
    make_success_response,
)


history_bp = Blueprint("user_history", __name__, url_prefix="/user-history")
CORS(history_bp, supports_credentials=True)


@history_bp.post("/")
async def store_user_history() -> Response:
    """
    # Json structure: Username of user that is currently logged in and the article on which he clicked

    .. code-block:: json

        {
            "articleLink": "https:foo.article/article1.html"
        }
    """

    schema = {
        "type": "object",
        "properties": {
            "articleLink": {
                "description": "Article on which the user clicked",
                "type": "string",
            },
        },
        "required": ["articleLink"],
    }

    data = request.get_json(silent=True)
    if not data:
        return make_response_from_error(HTTPStatus.BAD_REQUEST, ErrorKind.InvalidJson)

    try:
        validate(instance=data, schema=schema)
    except ValidationError as e:
        return make_response_from_error(
            HTTPStatus.BAD_REQUEST, ErrorKind.JsonValidationError, e.message
        )
    except SchemaError as e:
        print(f"jsonschema is invalid: {e.message}", file=sys.stderr)
        raise e

    db = await get_db()

    cookie = request.cookies.get("session")
    if cookie is None:
        return make_response_from_error(
            HTTPStatus.BAD_REQUEST,
            ErrorKind.CookieNotSet,
            "Cookie not present in request",
        )

    try:
        user_cookie = await db.usercookies.find_unique(
            where={"cookie": cookie}, include={"user": True}
        )
    except Exception:
        return make_response_from_error(
            HTTPStatus.INTERNAL_SERVER_ERROR,
            ErrorKind.ServerError,
        )

    if user_cookie is None or user_cookie.user is None:
        return make_response_from_error(
            HTTPStatus.BAD_REQUEST,
            ErrorKind.CookieNotFound,
        )

    user = user_cookie.user

    clicked_article = await db.newsarticles.find_first(
        where={"url": data["articleLink"]}, include={"labels": True}
    )

    if clicked_article is None:
        return make_response_from_error(
            HTTPStatus.INTERNAL_SERVER_ERROR,
            ErrorKind.ServerError,
        )

    labels: List[str] = []
    if clicked_article.labels is None:
        return make_response_from_error(
            HTTPStatus.INTERNAL_SERVER_ERROR,
            ErrorKind.ServerError,
        )

    for label in clicked_article.labels:
        labels.append(label.label)

    source = await db.newssources.find_unique(where={"id": clicked_article.source_id})

    if source is None:
        return make_response_from_error(
            HTTPStatus.INTERNAL_SERVER_ERROR,
            ErrorKind.ServerError,
        )

    # Url of the source,labels,user
    await db.userarticlehistory.create(
        data={
            "labels": labels,
            "user": {
                "connect": {
                    "id": user.id,
                }
            },
            "source_url": source.url,
        }
    )
    return make_success_response()
