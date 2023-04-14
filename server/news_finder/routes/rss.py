from flask import Blueprint, Response, request, make_response, jsonify
from urllib.parse import ParseResult, urlparse
from http import HTTPStatus
from jsonschema import SchemaError, validate, ValidationError
from prisma.errors import UniqueViolationError, RecordNotFoundError

from news_finder.db import get_db
from news_finder.utils.error_response import make_error_response, ResponseError

import sys

rss_bp = Blueprint("rss", __name__, url_prefix="/rss")


@rss_bp.get("/")
async def get_rss_feeds() -> Response:
    """
    Get a json with all the rss feeds and their news source

    # Feeds json structure:
    {
        "feeds": [
            {
                "source": "www.vrt.be",
                "feed": "https://www.vrt.be/vrtnws/nl.rss.articles.xml"
            }.
            ...
        ]
    }
    """

    db = await get_db()

    try:
        feeds = await db.rssentries.find_many(include={"source": True})
    except Exception as e:
        print(e.with_traceback(None), file=sys.stderr)
        return make_error_response(
            ResponseError.ServerError, "", HTTPStatus.INTERNAL_SERVER_ERROR
        )

    response: dict[str, list[dict[str, str]]] = {"feeds": []}
    for feed in feeds:
        assert (
            feed.source is not None
        ), "feed should always have a source associated with it"

        news_source = feed.source.name

        response["feeds"].append({"source": news_source, "feed": feed.feed})

    return make_response(jsonify(response), HTTPStatus.OK)


@rss_bp.post("/by-source/")
async def get_rss_feeds_by_source() -> Response:
    """
    Get a json with all the rss feeds belonging to a certain news source

    # Source json structure:
    {
        "source": "www.vrt.be"
    }

    # Feeds json structure:
    {
        "feeds": [
            "https://www.vrt.be/vrtnieuws/nl.rss.articles.xml",
            "https://www.vrt.be/vrtnieuws/en.rss.articles.xml".
            ...
        ]
    }
    """

    schema = {
        "type": "object",
        "properties": {
            "source": {
                "description": "source of the rss feeds",
                "type": "string",
            },
        },
        "required": ["source"],
    }

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

    try:
        source = await db.newssources.find_unique(
            where={
                "name": data["source"]
            },
            include={
                "rss": True
            }
        )
    except Exception as e:
        print(e.with_traceback(None), file=sys.stderr)
        return make_error_response(
            ResponseError.ServerError, "", HTTPStatus.INTERNAL_SERVER_ERROR
        )
    if source is None or source.rss is None:
        return make_error_response(
            ResponseError.ServerError, "", HTTPStatus.BAD_REQUEST
        )
    
    urls: list[str] = []
    for rss_entry in source.rss:
        urls.append(rss_entry.feed)

    response: dict[str, list[str]] = {"feeds": urls}

    return make_response(jsonify(response), HTTPStatus.OK)


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
        rss_feed = rss_feed.strip()

        # Extract news source and news source url from rss feed url
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
    """
    Delete rss feeds from the database

    # Feed json structure: (checked using schema validation)
    {
        "feeds": [
            "https://www.vrt.be/vrtnws/nl.rss.articles.xml",
            ...
        ]
    }
    """

    schema = {
        "type": "object",
        "properties": {
            "feeds": {
                "description": "list off rss feeds to be deleted",
                "type": "array",
                "items": {"type": "string"},
            },
        },
        "required": ["feeds"],
    }

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
    news_sources: set[str] = set()

    for rss_feed in data["feeds"]:
        entry = await db.rssentries.find_first(
            where={"feed": rss_feed}, include={"source": True}
        )

        if entry is not None:
            # Skip asserting or returning an error when no entry is found because the
            # record will not be found later on and an error will be raised then.
            assert (
                entry.source is not None
            ), "feed should always have a source associated with it"

            news_sources.add(entry.source.name)

        b.rssentries.delete(where={"feed": rss_feed})

    try:
        await b.commit()
    except RecordNotFoundError as e:
        return make_error_response(
            ResponseError.RecordNotFoundError,
            str(e.with_traceback(None)),
            HTTPStatus.BAD_REQUEST,
        )
    except Exception as e:
        print(e.with_traceback(None), file=sys.stderr)
        return make_error_response(
            ResponseError.ServerError, "", HTTPStatus.INTERNAL_SERVER_ERROR
        )

    # Delete news source if all feeds are deleted
    for news_source_name in news_sources:
        try:
            news_source = await db.newssources.find_first(
                where={"name": news_source_name}
            )
        except RecordNotFoundError as e:
            return make_error_response(
                ResponseError.ServerError,
                str(e.with_traceback(None)),
                HTTPStatus.INTERNAL_SERVER_ERROR,
            )

        if news_source is None:
            return make_error_response(
                ResponseError.ServerError, "", HTTPStatus.INTERNAL_SERVER_ERROR
            )
        if news_source.rss:
            try:
                await db.newssources.delete(where={"name": news_source_name})
            except RecordNotFoundError as e:
                return make_error_response(
                    ResponseError.ServerError,
                    str(e.with_traceback(None)),
                    HTTPStatus.INTERNAL_SERVER_ERROR,
                )

    return make_response("", HTTPStatus.OK)
