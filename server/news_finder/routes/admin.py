from flask import Blueprint, Response, request
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


@admin_bp.post("/status/")
async def is_admin() -> Response:
    """
    Check if a user is an admin.

    # Json structure: (checked using schema validation)

    .. code-block:: json

        {
            "name": "username"
        }
    """

    schema = {
        "type": "object",
        "properties": {
            "username": {
                "description": "User to be checked",
                "type": "string",
            }
        },
        "required": ["username"],
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

    try:
        user = await db.users.find_first(
            where={
                "username": data["username"].lower(),
            }
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

    if user is None:
        return make_response_from_error(
            HTTPStatus.BAD_REQUEST,
            ErrorKind.RecordNotFoundError,
        )

    return make_success_response(
        HTTPStatus.OK,
        {"admin": user.admin},
    )
