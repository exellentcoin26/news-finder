from flask import Blueprint, Response, request, make_response
from urllib.parse import ParseResult, urlparse
from http import HTTPStatus
from jsonschema import SchemaError, validate, ValidationError
from prisma.errors import UniqueViolationError, RecordNotFoundError

from news_finder.db import get_db
from news_finder.utils.error_response import make_error_response, ResponseError

import sys

rss_bp = Blueprint("rss", __name__, url_prefix="/rss")


schema = {
    "type": "object",
    "properties": {
        "feeds": {
            "description": "list off rss feeds to be added",
            "type": "array",
            "items": {"type": "string"},
        },
    },
    "required": ["feeds"],
}


@rss_bp.post("/")
async def add_rss_feed() -> Response:
    """
    Add rss feeds to database for scraping later on. The news source will be
    extracted from the hostname of the url.

    # Feed json structure: (checked using schema validation)
    {
        "feeds": [
            "https://www.vrt.be/vrtnws/nl.rss.articles.xml",
            ...
        ]
    }
    """

    data = request.get_json(silent=True)
    if not data:
        return make_error_response(
            ResponseError.InvalidJson, "", HTTPStatus.BAD_REQUEST
        )

    try:
        validate(instance=data, schema=schema)
    except ValidationError as e:
        return make_error_response(
            ResponseError.JsonValidationError, e.message, HTTPStatus.BAD_REQUEST
        )
    except SchemaError as e:
        print(f"jsonschema is invalid: {e.message}", file=sys.stderr)
        raise e

    db = await get_db()

    b = db.batch_()

    for rss_feed in data["feeds"]:
        # extract news source and news source url from rss feed url
        url_components: ParseResult = urlparse(rss_feed)

        news_source = url_components.netloc
        news_source_url = url_components.scheme + "://" + url_components.netloc

        # Update news-source with new rss entry if news-source already present,
        # else insert a new news-source with the rss feed.
        b.newssources.upsert(
            where={"name": news_source},
            data={
                "create": {
                    "name": news_source,
                    "url": news_source_url,
                    "rss": {"create": {"feed": rss_feed}},
                },
                "update": {
                    "rss": {
                        "create": [
                            {
                                "feed": rss_feed,
                            }
                        ]
                    }
                },
            },
        )

    try:
        await b.commit()
    except UniqueViolationError as e:
        return make_error_response(
            ResponseError.UniqueViolationError,
            str(e.with_traceback(None)),
            HTTPStatus.BAD_REQUEST,
        )
    except Exception as e:
        print(e.with_traceback(None), file=sys.stderr)
        return make_error_response(
            ResponseError.ServerError, "", HTTPStatus.INTERNAL_SERVER_ERROR
        )

    return make_response("", HTTPStatus.OK)

@rss_bp.delete("/")
async def delete_rss() -> Response:
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
        b.rssentries.delete(
            where={
                "feed": rss_feed #TODO: remove news source if it has no rss entries
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

