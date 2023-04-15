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
    RecordNotFoundError = 4
    CookieNotSet = 5
    CookieNotFound = 6
    UserAlreadyPresent = 7
    WrongPassword = 8
    IncorrectParameters = 9

    ServerError = 500

    def __str__(self) -> str:
        return self.name


def make_error_response(
    error: ResponseError, message: str, error_code: HTTPStatus
) -> Response:
    return make_response(jsonify({"error": str(error), "message": message}), error_code)
