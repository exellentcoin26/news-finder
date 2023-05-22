from flask import Blueprint, Response, request
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


history_bp = Blueprint("user", __name__, url_prefix="/user-history")


@history_bp.post("/")
async def store_user_history() -> Response:
    """
    # Json structure: Username of user that is currently logged in and the article on which he clicked

    .. code-block:: json

        {
            "username": "name",
            "articleLink": "https:foo.article/article1.html"
        }
    """

    schema = {
        "type": "object",
        "properties": {
            "username": {
                "description": "Name of the user that is currently logged in",
                "type": "string",
            },
            "articleLink": {
                "description": "Article on which the user clicked",
                "type": "string",
            },
        },
        "required": "username",
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

    user = await db.users.find_first(where={"username": data["username"]})
    clicked_article = await db.newsarticles.find_first(
        where={"url": data["articleLink"]}
    )

    if user is None or clicked_article is None:
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
