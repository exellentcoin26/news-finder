from flask import Blueprint, Response, request, make_response
from prisma import Prisma
from prisma.errors import UniqueViolationError 

from ..db import get_db
import secrets

user_bp = Blueprint("user", __name__, url_prefix="/user")


@user_bp.get("/")
def hello_user() -> Response:
    return Response("Hello, User!")


async def create_cookie_for_user(prisma: Prisma, user_id: int) -> str:
    user_cookie: str = secrets.token_hex(32)

    await prisma.usercookies.create(data={
        "cookie": user_cookie,
        "user_id": user_id
    })

    return user_cookie


@user_bp.post("/register")
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
    while cookie is None:
        try:
            cookie = await create_cookie_for_user(prisma, user.id)
        except UniqueViolationError:
            pass

    resp: Response
    resp = make_response("", 200)
    resp.set_cookie("session", cookie)

    return resp


@user_bp.post("/logout")
async def logout_user() -> Response:
    prisma = await get_db()
    cookie: str = request.cookies.get("session")

    await prisma.usercookies.delete(
        where={
            "cookie": cookie
        }
    )


    return make_response("", 200)
