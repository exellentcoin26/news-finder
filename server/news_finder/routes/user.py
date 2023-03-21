from flask import Blueprint, Response, request, make_response
from ..db import get_db
import secrets

user_bp = Blueprint("user", __name__, url_prefix="/user")


@user_bp.get("/")
def hello_user() -> Response:
    return Response("Hello, User!")

async def create_cookie_for_user(prisma, user_id):
    cookie = secrets.token_hex(32)

    await prisma.usercookies.create(data={
        "cookie": cookie,
        "user_id": user_id
    })

    return cookie



@user_bp.post("/register")
async def register_user():
    prisma = await get_db()
    data = request.get_json()
    username = data["username"]
    password = data["password"]
    cookie = secrets.token_hex(32)

    user = await prisma.users.find_first(
        where={'username': username}
    )

    if user is not None:
        return '', 409

    user = await prisma.users.create(data={
        "username": username
    })

    await prisma.userlogins.create(data={
        "password": password,
        "id": user.id
    })

    cookie = None
    while cookie is None:
        try:
            cookie = await create_cookie_for_user(prisma, user.id)
        except Exception:
            pass

    resp = make_response('', 200)
    resp.set_cookie('session', cookie)

    return resp, 200


@user_bp.post("/logout")
async def logout_user():
    prisma = await get_db()
    cookie = request.cookies.get('session')

    await prisma.usercookies.delete(
        where={
            'cookie': cookie
        }
    )

    return '', 200
