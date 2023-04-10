from flask import Blueprint, Response, request, make_response, jsonify
from prisma.errors import UniqueViolationError, RecordNotFoundError
from jsonschema import validate, SchemaError, ValidationError

import sys

from uuid import uuid4
from http import HTTPStatus

from server.news_finder.db import get_db
from server.news_finder.utils.error_response import make_error_response, ResponseError

from password_hash.password_hash import *
user_bp = Blueprint("user", __name__, url_prefix="/user")


async def create_cookie_for_user(user_id: int) -> str:
    cookie = str(uuid4())

    db = await get_db()
    await db.usercookies.create(data={"cookie": cookie, "user_id": user_id})

    return cookie


@user_bp.post("/")
async def register_user() -> Response:
    """
    Create a user.

    # Json structure: (checked using schema validation)
    {
        "username": "user1"
        "password": "qwerty"
    }
    """

    data = request.get_json(silent=True)
    if not data:
        return make_error_response(
            ResponseError.InvalidJson, "", HTTPStatus.BAD_REQUEST
        )

    schema = {
        "type": "object",
        "properties": {
            "username": {
                "description": "The username of the user to be created",
                "type": "string",
            },
            "password": {
                "description": "The password of the user to be created",
                "type": "string",
            },
        },
        "required": ["username", "password"],
    }

    try:
        validate(instance=data, schema=schema)
    except ValidationError as e:
        return make_error_response(
            ResponseError.JsonValidationError, e.message, HTTPStatus.BAD_REQUEST
        )
    except SchemaError as e:
        print(f"jsonschema is invalid: {e.message}", file=sys.stderr)
        raise e




    Ph = PasswordHasher()
    Ph.setPassword(data["password"])
    Ph.hash()

    username = data["username"].lower()
    HashedPassword = Ph.getHash()

    db = await get_db()



    existing_user = await db.users.find_first(where={"username": username})

    if existing_user is not None:
        return make_error_response(
            ResponseError.UserAlreadyPresent,
            "User already present in database",
            HTTPStatus.CONFLICT,
        )

    user = await db.users.create(data={"username": username})
    await db.userlogins.create(data={"password": HashedPassword, "id": user.id})


    cookie: str = ""
    while cookie == "":
        try:
            cookie = await create_cookie_for_user(user.id)
        except UniqueViolationError:
            pass

    resp = make_response("", HTTPStatus.OK)
    resp.set_cookie("session", cookie)

    return resp


@user_bp.post("/login/")
async def login_user() -> Response:
    """
    Log a user in.

    # Json structure: (checked using schema validation)
    {
        "username": "user1"
        "password": "qwerty"
    }
    """

    data = request.get_json(silent=True)
    if not data:
        return make_error_response(
            ResponseError.InvalidJson, "", HTTPStatus.BAD_REQUEST
        )

    schema = {
        "type": "object",
        "properties": {
            "username": {
                "description": "username for the user to be logged in",
                "type": "string",
            },
            "password": {
                "description": "password of the user to be logged in",
                "type": "string",
            },
        },
        "required": ["username", "password"],
    }

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
        user = await db.users.find_first(where={"username": data["username"].lower()})
    except RecordNotFoundError:
        return make_error_response(
            ResponseError.RecordNotFoundError, "", HTTPStatus.BAD_REQUEST
        )
    except Exception as e:
        print(e.with_traceback(None), file=sys.stderr)
        return make_error_response(
            ResponseError.ServerError, "", HTTPStatus.INTERNAL_SERVER_ERROR
        )

    if user is None:
        return make_error_response(
            ResponseError.RecordNotFoundError, "", HTTPStatus.BAD_REQUEST
        )

    try:
        user_login = await db.userlogins.find_first(
            where={"user": {"is": {"id": user.id}}}
        )
    except RecordNotFoundError:
        return make_error_response(
            ResponseError.ServerError, "", HTTPStatus.INTERNAL_SERVER_ERROR
        )
    except Exception as e:
        print(e.with_traceback(None), file=sys.stderr)
        return make_error_response(
            ResponseError.ServerError, "", HTTPStatus.INTERNAL_SERVER_ERROR
        )

    if user_login is None:
        return make_error_response(
            ResponseError.ServerError, "", HTTPStatus.INTERNAL_SERVER_ERROR
        )

    if user_login.password != data["password"]:
        return make_error_response(
            ResponseError.WrongPassword, "", HTTPStatus.UNAUTHORIZED
        )

    cookie: str = ""
    while cookie == "":
        try:
            cookie = await create_cookie_for_user(user.id)
        except UniqueViolationError:
            pass

    resp = make_response("", HTTPStatus.OK)
    resp.set_cookie("session", cookie)
    return resp


@user_bp.post("/logout/")
async def logout_user() -> Response:
    """
    Log a user out.
    """

    cookie = request.cookies.get("session")
    if cookie is None:
        return make_error_response(
            ResponseError.CookieNotSet,
            "Cookie not present in request",
            HTTPStatus.BAD_REQUEST,
        )

    db = await get_db()

    try:
        await db.usercookies.delete(where={"cookie": cookie})
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

    return make_response("", HTTPStatus.OK)


@user_bp.post("/status/")
async def login_status() -> Response:
    """
    Check whether a user is logged in based on their cookie.
    """

    cookie = request.cookies.get("session")
    if cookie is None:
        return make_response(jsonify({"logged_in": False}), HTTPStatus.OK)

    db = await get_db()

    try:
        await db.usercookies.find_unique(where={"cookie": cookie})
    except RecordNotFoundError:
        return make_response(jsonify({"logged_in": False}), HTTPStatus.OK)
    except Exception:
        return make_error_response(
            ResponseError.ServerError, "", HTTPStatus.INTERNAL_SERVER_ERROR
        )

    return make_response(jsonify({"logged_in": True}), HTTPStatus.OK)
