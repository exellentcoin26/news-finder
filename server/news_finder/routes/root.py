from flask import Response, Blueprint
from http import HTTPStatus

from news_finder.response import make_success_response

root_bp = Blueprint("root", __name__, url_prefix="/")


# route for docker to check whether the server is up and running
@root_bp.get("/healthcheck")
def healthcheck() -> Response:
    return make_success_response(
        HTTPStatus.OK,
    )
