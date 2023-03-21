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


async def create_cookie_for_user(prisma: Prisma, user_id: int) -> str:
    user_cookie: str = str(uuid4())

    await prisma.usercookies.create(data={
        "cookie": user_cookie,
        "user_id": user_id
    })

    return user_cookie


@user_bp.post("/")
async def register_user() -> Response:
    prisma = await get_db()
    data = request.get_json()
    username: str = data["username"]
    password: str = data["password"]

    user = await prisma.users.find_first(
        where={"username": username}
    )

    if user is not None:
        return make_response("", 409)

    user = await prisma.users.create(data={
        "username": username
    })

    await prisma.userlogins.create(data={
        "password": password,
        "id": user.id
    })

    cookie = ""
    while cookie == "":
        try:
            cookie = await create_cookie_for_user(prisma, user.id)
        except UniqueViolationError:
            pass

    resp: Response
    resp = make_response("", HTTPStatus.OK)
    resp.set_cookie("session", cookie)

    return resp


@user_bp.post("/logout")
async def logout_user() -> Response:
    prisma = await get_db()
    cookie: str | None = request.cookies.get("session")

    if cookie is None:
        return make_error_response(ResponseError.CookieNotSet, "Cookie header not set in request", HTTPStatus.BAD_REQUEST)


    try:
        await prisma.usercookies.delete(
            where={
                "cookie": cookie
            }
        )
    except RecordNotFoundError:
        return make_error_response(ResponseError.CookieNotFound, "Cookie is not found in the database", HTTPStatus.BAD_REQUEST)
    except Exception:
        return make_error_response(ResponseError.ServerError, "", HTTPStatus.INTERNAL_SERVER_ERROR)

    return make_response("", 200)
