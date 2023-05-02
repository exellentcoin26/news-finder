from flask import Blueprint, Response, request
from flask_cors import CORS
from http import HTTPStatus
from jsonschema import SchemaError, validate, ValidationError
from prisma.errors import RecordNotFoundError

from news_finder.db import get_db
from news_finder.response import (
    make_response_from_error,
    ErrorKind,
    make_success_response,
)

import sys

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")
CORS(admin_bp, supports_credentials=True)

@admin_bp.post("/")
async def add_admin() -> Response:
    """
    Change the "admin" field of one or more user(s) to true

    # Json structure: (checked using schema validation)

    .. code-block:: json

        {
            "names": [
                "username",
                ...
            ]
        }
    """

    schema = {
        "type": "object",
        "properties": {
            "usernames": {
                "description": "List of users to be made admin",
                "type": "array",
                "items": {"type": "string"},
            }
        },
        "required": ["usernames"],
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
    b = db.batch_()

    for user in data["usernames"]:
        b.users.update(where={"username": user.lower()}, data={"admin": True})

    try:
        await b.commit()
    except RecordNotFoundError as e:
        return make_response_from_error(
            HTTPStatus.BAD_REQUEST,
            ErrorKind.RecordNotFoundError,
            str(e.with_traceback(None)),
        )
    except Exception as e:
        print(e.with_traceback(None), file=sys.stderr)
        return make_response_from_error(
            HTTPStatus.INTERNAL_SERVER_ERROR,
            ErrorKind.ServerError,
        )

    return make_success_response()


@admin_bp.get("/")
async def is_admin() -> Response:
    """
    Check if a user is an admin based on the cookie.
    """

    cookie = request.cookies.get("session")
    if not cookie:
        return make_success_response(HTTPStatus.OK, {"admin": False})

    db = await get_db()

    try:
        cookie_entry = await db.usercookies.find_unique(
            where={"cookie": cookie},
            include={"user": True},
        )
    except RecordNotFoundError as e:
        return make_response_from_error(
            HTTPStatus.BAD_REQUEST,
            ErrorKind.RecordNotFoundError,
            str(e.with_traceback(None)),
        )
    except Exception as e:
        print(e.with_traceback(None), file=sys.stderr)
        return make_response_from_error(
            HTTPStatus.INTERNAL_SERVER_ERROR,
            ErrorKind.ServerError,
        )

    if cookie_entry is None:
        return make_response_from_error(
            HTTPStatus.BAD_REQUEST,
            ErrorKind.RecordNotFoundError
        )
    if cookie_entry.user is None:
        return make_response_from_error(
            HTTPStatus.BAD_REQUEST,
            ErrorKind.RecordNotFoundError,
        )

    return make_success_response(HTTPStatus.OK, {"admin": cookie_entry.user.admin})
