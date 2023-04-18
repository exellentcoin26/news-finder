from flask import Blueprint, Response, make_response
from werkzeug.exceptions import BadRequest, HTTPException

error_bp = Blueprint("error", __name__)

# TODO: Rework to use new response interface


@error_bp.app_errorhandler(404)
def page_not_found(_: Exception) -> Response:
    return Response("<h1>404 - page not found</h1>", status=404)


@error_bp.app_errorhandler(BadRequest)
def bad_request(_: Exception) -> Response:
    return Response("<h1>400 - bad request</h1>", status=400)


@error_bp.app_errorhandler(Exception)
def generic_error(e: Exception) -> Response:
    if isinstance(e, HTTPException):
        return make_response(e)

    print(e.with_traceback(None))

    return Response("<h1>500 - error occurred</h1>", status=500)
