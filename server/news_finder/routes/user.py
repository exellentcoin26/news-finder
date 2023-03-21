from flask import Blueprint, Response, request, make_response
from prisma import Prisma
from prisma.errors import UniqueViolationError, RecordNotFoundError

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


@user_bp.post("/logout")
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
