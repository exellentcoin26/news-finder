from flask import Blueprint, Response, make_response
from werkzeug.exceptions import HTTPException

error_bp = Blueprint("error", __name__)


@error_bp.app_errorhandler(404)
def page_not_found(_: Exception) -> Response:
    return Response("page not found", status=404)


@error_bp.app_errorhandler(Exception)
def generic_error(e: Exception) -> Response:
    if isinstance(e, HTTPException):
        return make_response(e)

    return Response("error occurred", status=500)
