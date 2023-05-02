from flask import Blueprint, Response
from http import HTTPStatus

from news_finder.db import get_db
from news_finder.response import (
    make_response_from_error,
    ErrorKind,
    make_success_response,
)

import sys

source_bp = Blueprint("source", __name__, url_prefix="/source")


@source_bp.get("/")
async def get_sources() -> Response:
    """
    Get a json with all the news sources

    # Feeds json structure:
    {
        "sources": ["www.vrt.be", ...]
    }
    """

    db = await get_db()

    try:
        sources = await db.newssources.find_many()
    except Exception as e:
        print(e.with_traceback(None), file=sys.stderr)
        return make_response_from_error(
            HTTPStatus.INTERNAL_SERVER_ERROR,
            ErrorKind.ServerError,
        )

    response: dict[str, list[str]] = {"sources": []}
    for source in sources:
        response["sources"].append(source.name)

    return make_success_response(HTTPStatus.OK, response)
