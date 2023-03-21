from flask import Response, make_response, jsonify
from http import HTTPStatus

from enum import Enum


class ResponseError(Enum):
    """
    Error enum used for returning a response
    """

    # Object is not JSON.
    InvalidJson = 0
    # JSON object does not comply with schema.
    JsonValidationError = 2
    UniqueViolationError = 3
    CookieNotSet = 4
    CookieNotFound = 5
    UserAlreadyPresent = 6

    ServerError = 500

    def __str__(self) -> str:
        return self.name


def make_error_response(
    error: ResponseError, message: str, error_code: HTTPStatus
) -> Response:
    return make_response(jsonify({"error": str(error), "message": message}), error_code)
