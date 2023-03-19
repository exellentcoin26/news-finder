from flask import Blueprint, Response, request, make_response
from http import HTTPStatus
from jsonschema import SchemaError, validate, ValidationError
from prisma.errors import RecordNotFoundError

from news_finder.db import get_db
from news_finder.utils.error_response import make_error_response, ResponseError

import sys

delete_rss_bp = Blueprint("rss", __name__, url_prefix="/deleterss")


schema = {
    "type": "object",
    "properties": {
        "feeds": {
            "description": "list off rss feeds to be deleted",
            "type": "array",
            "items": {
                "type": "string"
            }
        },
    },
    "required": ["feeds"]
}


@delete_rss_bp.post("/")
async def delete_rss_feed() -> Response:
    data = request.get_json(silent=True)
    if not data:
        return make_error_response(
            ResponseError.InvalidJson, "", HTTPStatus.BAD_REQUEST
        )

    try:
        validate(instance=data, schema=schema)
    except ValidationError as e:
        return make_error_response(
            ResponseError.JsonValidationError, e.message,
            HTTPStatus.BAD_REQUEST
        )
    except SchemaError as e:
        print(f"jsonschema is invalid: {e.message}", file=sys.stderr)
        raise e

    db = await get_db()

    b = db.batch_()

    for rss_feed in data["feeds"]:
        # extract news source from rss feed url
        url_components: ParseResult = urlparse(rss_feed)
        news_source = url_components.netloc
        b.newssources.delete(
            where={
                "name": news_source
            }
        )

    try:
        await b.commit()
    except RecordNotFoundError as e:
        return make_error_response(
            ResponseError.RecordNotFoundError,
            str(e.with_traceback(None)), HTTPStatus.BAD_REQUEST
        )
    except Exception as e:
        print(e.with_traceback(None), file=sys.stderr)
        return make_error_response(
            ResponseError.ServerError, "",
            HTTPStatus.INTERNAL_SERVER_ERROR
        )

    return make_response("", HTTPStatus.OK)
