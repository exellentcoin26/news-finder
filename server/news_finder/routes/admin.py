from flask import Blueprint, Response, request, make_response
from http import HTTPStatus
from jsonschema import SchemaError, validate, ValidationError
from prisma.errors import RecordNotFoundError

from news_finder.db import get_db
from news_finder.utils.error_response import make_error_response, ResponseError

import sys

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

schema = {
    "type": "object",
    "properties": {
        "admin": {
            "description": "List of users to be made admin",
            "type": "array",
            "items": {
                "type": "string"
            }
        }
    },
    "required": ["admins"]
}


@admin_bp.post("/")
async def add_admin() -> Response:
    """
    Change the "admin" field of one or more user(s) to true

    # Admin json structure: (checked using schema validation)
    {
        "admin": [
            "username",
            ...
        ]
    }
    """

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

    for user in data["admin"]:
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
