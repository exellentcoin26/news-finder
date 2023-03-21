from flask import Blueprint, Response, request, make_response, jsonify
from http import HTTPStatus
from jsonschema import SchemaError, validate, ValidationError
from prisma.errors import RecordNotFoundError

from news_finder.db import get_db
from news_finder.utils.error_response import make_error_response, ResponseError

import sys

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.post("/")
async def add_admin() -> Response:
    """
    Change the "admin" field of one or more user(s) to true

    # Json structure: (checked using schema validation)
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
                "items": {
                    "type": "string"
                }
            }
        },
        "required": ["usernames"]
    }

    data = request.get_json(silent=True)
    if not data:
        return make_error_response(
            ResponseError.InvalidJson, "", HTTPStatus.BAD_REQUEST
        )

    try:
        validate(instance=data, schema=schema)
    except ValidationError as e:
        return make_error_response(
            ResponseError.JsonValidationError, e.message, HTTPStatus.BAD_REQUEST
        )
    except SchemaError as e:
        print(f"jsonschema is invalid: {e.message}", file=sys.stderr)
        raise e

    db = await get_db()
    b = db.batch_()

    for user in data["usernames"]:
        b.users.update(
            where={
                "username": user
            },
            data={
                "admin": True
            }
        )

    try:
        await b.commit()
    except RecordNotFoundError as e:
        return make_error_response(
            ResponseError.RecordNotFoundError,
            str(e.with_traceback(None)), HTTPStatus.BAD_REQUEST
        )
    except Exception as e:
        print(e.with_traceback(None), file=sys.stderr)
        return make_error_response(
            ResponseError.ServerError, "",
            HTTPStatus.INTERNAL_SERVER_ERROR
        )

    return make_response("", HTTPStatus.OK)


@admin_bp.post("/is-admin")
async def is_admin() -> Response:
    """
    Check if a user is an admin

    # Json structure: (checked using schema validation)
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
        "required": ["username"]
    }

    data = request.get_json(silent=True)
    if not data:
        return make_error_response(
            ResponseError.InvalidJson, "", HTTPStatus.BAD_REQUEST
        )

    try:
        validate(instance=data, schema=schema)
    except ValidationError as e:
        return make_error_response(
            ResponseError.JsonValidationError, e.message, HTTPStatus.BAD_REQUEST
        )
    except SchemaError as e:
        print(f"jsonschema is invalid: {e.message}", file=sys.stderr)
        raise e

    db = await get_db()

    try:
        user = await db.users.find_first(
            where={
                "username": data["username"],
            }
        )
    except RecordNotFoundError as e:
        return make_error_response(
            ResponseError.RecordNotFoundError,
            str(e.with_traceback(None)), HTTPStatus.BAD_REQUEST
        )
    except Exception as e:
        print(e.with_traceback(None), file=sys.stderr)
        return make_error_response(
            ResponseError.ServerError, "",
            HTTPStatus.INTERNAL_SERVER_ERROR
        )

    return make_response(jsonify({"admin": user.admin}), HTTPStatus.OK)
