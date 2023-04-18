from flask import Response, make_response, jsonify
from http import HTTPStatus
from typing import List, Optional, Dict, Any

from enum import Enum


class ErrorKind(Enum):
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
    NewsSourceNotFound = 10

    ServerError = 500

    def __str__(self) -> str:
        return self.name


class Error:
    def __init__(self, kind: ErrorKind, message: str = "") -> None:
        self.kind: ErrorKind = kind
        self.message: str = message


class ResponseBody:
    def __init__(
        self,
        status: HTTPStatus,
        data: Optional[Dict[str, Any]],
        errors: Optional[List[Error]] = None,
    ) -> None:
        self.status: HTTPStatus = status
        self.errors: List[Error] = errors or []
        self.data: Dict[str, Any] = data or {}

    def serialize(
        self,
    ) -> Dict[str, HTTPStatus | List[Dict[str, str]] | Dict[str, Any]]:
        """
        Serialize response body into json serializable object.
        """

        return {
            "status": self.status,
            "errors": [
                {"kind": str(error.kind), "message": error.message}
                for error in self.errors
            ],
            "data": self.data,
        }

    def make_response(self) -> Response:
        return make_response(jsonify(self.serialize()), self.status)


def make_response_from_error(
    error_code: HTTPStatus, error: ErrorKind, message: str = ""
) -> Response:
    return ResponseBody(error_code, None, [Error(error, message)]).make_response()


def make_response_from_errors(
    error_code: HTTPStatus,
    errors: List[Error],
) -> Response:
    return ResponseBody(error_code, None, errors).make_response()


def make_success_response(
    status: HTTPStatus = HTTPStatus.OK, data: Optional[Dict[str, Any]] = None
) -> Response:
    return ResponseBody(status, data).make_response()
