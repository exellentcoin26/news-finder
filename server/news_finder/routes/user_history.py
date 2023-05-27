from flask import Blueprint, Response, request
from flask_cors import CORS
from http import HTTPStatus
from jsonschema import SchemaError, validate, ValidationError
import sys
from typing import List, Set

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

    if clicked_article is None or clicked_article.labels is None:
        return make_response_from_error(
            HTTPStatus.INTERNAL_SERVER_ERROR,
            ErrorKind.ServerError,
        )

    label_source_history = await db.userlabelhistory.find_unique(
        where={"user_id": user.id}
    )
    label_set: Set[str] = set(
        [] if label_source_history is None else label_source_history.labels
    )

    for label in clicked_article.labels:
        label_set.add(label.label)

    labels: List[str] = list(label_set)

    source = await db.newssources.find_unique(where={"id": clicked_article.source_id})

    if source is None:
        return make_response_from_error(
            HTTPStatus.INTERNAL_SERVER_ERROR,
            ErrorKind.ServerError,
        )

    # Url of the source,labels,user
    await db.userlabelhistory.upsert(
        where={"user_id": user.id},
        data={
            "create": {
                "labels": labels,
                "user": {
                    "connect": {
                        "id": user.id,
                    }
                },
            },
            "update": {"labels": {"set": labels}},
        },
    )
    await db.userarticlehistory.upsert(
        where={
            "user_id_article_id": {"user_id": user.id, "article_id": clicked_article.id}
        },
        data={
            "create": {
                "user": {"connect": {"id": user.id}},
                "article": {"connect": {"id": clicked_article.id}},
            },
            "update": {},
        },
    )
    await db.usersourcehistory.upsert(
        where={"user_id_source_id": {"user_id": user.id, "source_id": source.id}},
        data={
            "create": {
                "user": {"connect": {"id": user.id}},
                "source": {"connect": {"id": source.id}},
            },
            "update": {},
        },
    )

    return make_success_response()
