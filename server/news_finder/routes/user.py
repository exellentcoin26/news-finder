from flask import Blueprint, Response, request, make_response
from prisma import Prisma
from prisma.errors import UniqueViolationError, RecordNotFoundError
from jsonschema import validate, SchemaError, ValidationError

import sys

from uuid import uuid4
from http import HTTPStatus

from news_finder.db import get_db
from news_finder.utils.error_response import make_error_response, ResponseError

user_bp = Blueprint("user", __name__, url_prefix="/user")


@user_bp.get("/")
def hello_user() -> Response:
    return Response("Hello, User!")


async def create_cookie_for_user(prisma: Prisma, user_id: int):
    cookie = str(uuid4())

    await prisma.usercookies.create(data={"cookie": cookie, "user_id": user_id})

    return cookie


@user_bp.post("/")
async def register_user() -> Response:
    prisma: Prisma = await get_db()

    data = request.get_json(silent=True)
    if not data:
        return make_error_response(
            ResponseError.InvalidJson, "", HTTPStatus.BAD_REQUEST
        )

    # TODO: add schema validation

    username = data["username"]
    password = data["password"]

    user = await prisma.users.find_first(where={"username": username})

    if user is not None:
        return make_error_response(
            ResponseError.UserAlreadyPresent,
            "User already present in database",
            HTTPStatus.CONFLICT,
        )

    user = await prisma.users.create(data={"username": username})

    await prisma.userlogins.create(data={"password": password, "id": user.id})

    cookie: str = ""
    while cookie == "":
        try:
            cookie = await create_cookie_for_user(prisma, user.id)
        except UniqueViolationError:
            pass

    resp = make_response("", HTTPStatus.OK)
    resp.set_cookie("session", cookie)

    return resp


@user_bp.post("/login/")
async def login_user() -> Response:
    schema = {
        "type": "object",
        "properties": {
            "username": {
                "description": "username for the user to be logged in",
                "type": "string",
            },
            "password": {
                "description": "password of the user to be logged in",
                "type": "string"
            },
            "cookie": {
                "description": "session cookie",
                "type": "string"
            }
        },
        "required": ["username", "password", "cookie"],
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
                "username": data["username"]
            }
        )
    except RecordNotFoundError:
        return make_error_response(
            ResponseError.RecordNotFoundError, "",
            HTTPStatus.BAD_REQUEST
        )
    except Exception as e:
        print(e.with_traceback(None), file=sys.stderr)
        return make_error_response(
            ResponseError.ServerError, "", HTTPStatus.INTERNAL_SERVER_ERROR
        )

    if user is None:
        return make_error_response(
            ResponseError.RecordNotFoundError, "",
            HTTPStatus.BAD_REQUEST
        )

    try:
        password = await db.userlogins.find_first(
            where={
                "user": {
                    "is": {
                        "id": user.id
                    }
                }
            }
        )
    except RecordNotFoundError:
        return make_error_response(
            ResponseError.RecordNotFoundError, "",
            HTTPStatus.BAD_REQUEST
        )
    except Exception as e:
        print(e.with_traceback(None), file=sys.stderr)
        return make_error_response(
            ResponseError.ServerError, "", HTTPStatus.INTERNAL_SERVER_ERROR
        )

    if password is None:
        return make_error_response(
            ResponseError.RecordNotFoundError, "",
            HTTPStatus.BAD_REQUEST
        )

    if password.password != data["password"]:
        return make_error_response(
            ResponseError.WrongPassword, "",
            HTTPStatus.UNAUTHORIZED
        )

    await db.users.update(
        where={
            "username": data["username"]
        },
        data={
            "cookies": {
                "create": [{
                    "cookie": data["cookie"]
                }]
            }
        }
    )

    return make_response("", HTTPStatus.OK)


@user_bp.post("/logout/")
async def logout_user() -> Response:
    prisma = await get_db()

    cookie = request.cookies.get("session")
    if cookie is None:
        return make_error_response(
            ResponseError.CookieNotSet,
            "Cookie not present in request",
            HTTPStatus.BAD_REQUEST,
        )

    try:
        await prisma.usercookies.delete(where={"cookie": cookie})
    except RecordNotFoundError:
        return make_error_response(
            ResponseError.CookieNotFound,
            "Cookie present in header not found in database",
            HTTPStatus.BAD_REQUEST,
        )
    except Exception:
        return make_error_response(
            ResponseError.ServerError, "", HTTPStatus.INTERNAL_SERVER_ERROR
        )

    return make_response(HTTPStatus.OK)
