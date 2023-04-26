import sys
from http import HTTPStatus
from typing import List
from uuid import uuid4

from argon2 import PasswordHasher
from argon2.exceptions import VerificationError, VerifyMismatchError, InvalidHash
from flask import Blueprint, Response, request
from flask_cors import CORS
from jsonschema import validate, SchemaError, ValidationError
from prisma.errors import UniqueViolationError, RecordNotFoundError

from news_finder.db import get_db
from news_finder.response import (
    make_response_from_error,
    make_response_from_errors,
    ErrorKind,
    Error,
    make_success_response,
)

user_bp = Blueprint("user", __name__, url_prefix="/user")

CORS(user_bp, supports_credentials=True)


async def create_cookie_for_user(user_id: int) -> str:
    """
    Tries to generate cookie for user and inserts into database.
    """

    cookie = str(uuid4())

    db = await get_db()
    await db.usercookies.create(data={"cookie": cookie, "user_id": user_id})

    return cookie


@user_bp.post("/")
async def register_user() -> Response:
    """
    Create a user.

    # Json structure: (checked using schema validation)

    .. code-block:: json

        {
            "username": "user1"
            "password": "qwerty"
        }
    """

    data = request.get_json(silent=True)
    if not data:
        return make_response_from_error(
            HTTPStatus.BAD_REQUEST,
            ErrorKind.InvalidJson,
        )

    schema = {
        "type": "object",
        "properties": {
            "username": {
                "description": "The username of the user to be created",
                "type": "string"
            },
            "password": {
                "description": "The password of the user to be created",
                "type": "string"
            },
        },
        "required": ["username", "password"],
    }

    try:
        validate(instance=data, schema=schema)
    except ValidationError as e:
        return make_response_from_error(
            HTTPStatus.BAD_REQUEST,
            ErrorKind.JsonValidationError,
            e.message,
        )
    except SchemaError as e:
        print(f"jsonschema is invalid: {e.message}", file=sys.stderr)
        raise e

    ph = PasswordHasher()

    username = data["username"].lower()
    password = data["password"]

    errors: List[Error] = []
    if len(username) == 0:
        error_username = Error(ErrorKind.UsernameToShort, "Username cannot be empty")
        errors.append(error_username)
    if len(password) == 0:
        error_password = Error(ErrorKind.PasswordToShort, "Password cannot be empty")
        errors.append(error_password)
    if len(errors) != 0:
        return make_response_from_errors(HTTPStatus.BAD_REQUEST, errors)
    hashed_password = ph.hash(password)

    db = await get_db()

    existing_user = await db.users.find_first(where={"username": username})

    if existing_user is not None:
        return make_response_from_error(
            HTTPStatus.CONFLICT,
            ErrorKind.UserAlreadyPresent,
            "User already present in database",
        )

    user = await db.users.create(data={"username": username})
    await db.userlogins.create(data={"password": hashed_password, "id": user.id})

    cookie: str = ""
    while cookie == "":
        try:
            cookie = await create_cookie_for_user(user.id)
        except UniqueViolationError:
            pass

    resp = make_success_response()
    resp.set_cookie("session", cookie, samesite="lax")

    return resp


@user_bp.delete("/")
async def delete_user():
    """
    Delete a user.

    # Json structure: (checked using schema validation)

    .. code-block:: json

        {
            "username": "user1"
        }
    """
    data = request.get_json(silent=True)
    if not data:
        return make_response_from_error(
            HTTPStatus.BAD_REQUEST,
            ErrorKind.InvalidJson,
        )

    schema = {
        "type": "object",
        "properties": {
            "username": {
                "description": "The username of the user to be deleted",
                "type": "string",
            },
        },
        "required": ["username"],
    }

    try:
        validate(instance=data, schema=schema)
    except ValidationError as e:
        return make_response_from_error(
            HTTPStatus.BAD_REQUEST, ErrorKind.JsonValidationError, e.message
        )
    except SchemaError as e:
        print(f"jsonschema is invalid: {e.message}", file=sys.stderr)
        raise e

    username = data["username"].lower()

    db = await get_db()

    try:
        user = await db.users.find_unique(where={"username": username})
    except Exception as e:
        print(e.with_traceback(None), file=sys.stderr)
        return make_response_from_error(
            HTTPStatus.INTERNAL_SERVER_ERROR,
            ErrorKind.ServerError,
        )

    if user is None:
        return make_response_from_error(
            HTTPStatus.BAD_REQUEST,
            ErrorKind.UserDoesNotExist,
        )

    try:
        await db.users.delete(where={"username": username})
    except Exception as e:
        print(e.with_traceback(None), file=sys.stderr)
        return make_response_from_error(
            HTTPStatus.INTERNAL_SERVER_ERROR,
            ErrorKind.ServerError,
        )

    return make_success_response()


@user_bp.post("/login/")
async def login_user() -> Response:
    """
    Log a user in.

    # Json structure: (checked using schema validation)

    .. code-block:: json

        {
            "username": "user1"
            "password": "qwerty"
        }
    """

    data = request.get_json(silent=True)
    if not data:
        return make_response_from_error(
            HTTPStatus.BAD_REQUEST,
            ErrorKind.InvalidJson,
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
        return make_response_from_error(
            HTTPStatus.BAD_REQUEST,
            ErrorKind.JsonValidationError,
            e.message,
        )
    except SchemaError as e:
        print(f"jsonschema is invalid: {e.message}", file=sys.stderr)
        raise e

    db = await get_db()

    try:
        user = await db.users.find_first(where={"username": data["username"].lower()})
    except Exception as e:
        # Note: Catching `RecordNotFoundError` is not needed because this is not thrown
        # for `find_first`
        print(e.with_traceback(None), file=sys.stderr)
        return make_response_from_error(
            HTTPStatus.INTERNAL_SERVER_ERROR,
            ErrorKind.ServerError,
        )

    if user is None:
        return make_response_from_error(
            HTTPStatus.BAD_REQUEST,
            ErrorKind.IncorrectCredentials,
            "Wrong combination of username and/or password",
        )

    try:
        user_login = await db.userlogins.find_first(
            where={"user": {"is": {"id": user.id}}}
        )
    except RecordNotFoundError:
        return make_response_from_error(
            HTTPStatus.INTERNAL_SERVER_ERROR,
            ErrorKind.ServerError,
        )
    except Exception as e:
        print(e.with_traceback(None), file=sys.stderr)
        return make_response_from_error(
            HTTPStatus.INTERNAL_SERVER_ERROR,
            ErrorKind.ServerError,
        )

    # Should be ok to assert because prisma would have thrown a `RecordNotFoundError`.
    assert user_login is not None

    ph = PasswordHasher()

    try:
        ph.verify(user_login.password, data["password"])
    except VerifyMismatchError:
        return make_response_from_error(
            HTTPStatus.UNAUTHORIZED,
            ErrorKind.IncorrectCredentials,
            "Wrong combination of username and/or password",
        )
    except InvalidHash as e:
        print(f"invalid hash: {user_login.password}", file=sys.stderr)
        raise e
    except VerificationError as e:
        print(e.with_traceback(None), file=sys.stderr)
        raise e
    except Exception as e:
        print(e.with_traceback(None), file=sys.stderr)
        return make_response_from_error(
            HTTPStatus.INTERNAL_SERVER_ERROR, ErrorKind.ServerError
        )

    cookie: str = ""
    while cookie == "":
        try:
            cookie = await create_cookie_for_user(user.id)
        except UniqueViolationError:
            pass

    resp = make_success_response()
    resp.set_cookie("session", cookie, samesite="lax")

    return resp


@user_bp.post("/logout/")
async def logout_user() -> Response:
    """
    Log a user out.
    """

    cookie = request.cookies.get("session")
    if cookie is None:
        return make_response_from_error(
            HTTPStatus.BAD_REQUEST,
            ErrorKind.CookieNotSet,
            "Cookie not present in request",
        )

    db = await get_db()

    try:
        await db.usercookies.delete(where={"cookie": cookie})
    except RecordNotFoundError:
        return make_response_from_error(
            HTTPStatus.BAD_REQUEST,
            ErrorKind.CookieNotFound,
            "Cookie present in header not found in database",
        )
    except Exception:
        return make_response_from_error(
            HTTPStatus.INTERNAL_SERVER_ERROR,
            ErrorKind.ServerError,
        )

    return make_success_response()


@user_bp.post("/status/")
async def login_status() -> Response:
    """
    Check whether a user is logged in based on their cookie.
    """

    cookie = request.cookies.get("session")
    if cookie is None:
        return make_success_response(HTTPStatus.OK, {"logged_in": False})

    db = await get_db()

    try:
        await db.usercookies.find_unique(where={"cookie": cookie})
    except RecordNotFoundError:
        return make_success_response(HTTPStatus.OK, {"logged_in": False})
    except Exception:
        return make_response_from_error(
            HTTPStatus.INTERNAL_SERVER_ERROR,
            ErrorKind.ServerError,
        )

    return make_success_response(HTTPStatus.OK, {"logged_in": True})
