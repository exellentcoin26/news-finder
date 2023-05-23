from flask import Blueprint, Response, request
from urllib.parse import ParseResult, urlparse
from http import HTTPStatus
from jsonschema import SchemaError, validate, ValidationError
from prisma.errors import UniqueViolationError
from typing import Dict, List

from validators.url import url as validate_url  # type: ignore

from prisma.models import RssEntries
from prisma.types import RssEntriesCreateWithoutRelationsInput

from news_finder.db import get_db
from news_finder.response import (
    make_response_from_error,
    ErrorKind,
    make_success_response,
)

import sys

rss_bp = Blueprint("rss", __name__, url_prefix="/rss")


@rss_bp.get("/")
async def get_rss_feeds() -> Response:
    """
    Get a json with all the rss feeds and their news source

    # Feeds json structure:

    .. code-block:: json

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
    # pyright: ignore
    source = request.args.get("source") or None

    db = await get_db()

    if source is not None:
        try:
            source = await db.newssources.find_unique(
                where={"name": source}, include={"rss": True}
            )
        except Exception as e:
            print(e.with_traceback(None), file=sys.stderr)
            return make_response_from_error(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                ErrorKind.ServerError,
            )

        if source is None or source.rss is None:
            return make_response_from_error(
                HTTPStatus.BAD_REQUEST, ErrorKind.NewsSourceNotFound
            )

        rss_feeds: List[Dict[str, str]] = []
        for rss_entry in source.rss:
            rss_feeds.append(
                {"source": source.name, "feed": rss_entry.feed, "name": rss_entry.name}
            )

        response_source: Dict[str, List[Dict[str, str]]] = {"feeds": rss_feeds}

        return make_success_response(HTTPStatus.OK, response_source)
    else:
        try:
            feeds: List[RssEntries] = await db.rssentries.find_many(
                include={"source": True}
            )
        except Exception as e:
            print(e.with_traceback(None), file=sys.stderr)
            return make_response_from_error(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                ErrorKind.ServerError,
            )

        response: dict[str, list[dict[str, str]]] = {"feeds": []}
        for feed in feeds:
            assert (
                feed.source is not None
            ), "feed should always have a source associated with it"

            news_source = feed.source.name

            response["feeds"].append(
                {"source": news_source, "feed": feed.feed, "name": feed.name}
            )

        return make_success_response(HTTPStatus.OK, response)


@rss_bp.post("/")
async def add_rss_feed() -> Response:
    """
    Add rss feeds to database for scraping later on. The news source will be
    extracted from the hostname of the url.

    # Feed json structure: (checked using schema validation)

    .. code-block:: json

        {
            "name": "VRT Wereld nieuws",
            "feed": "https://www.vrt.be/vrtnws/nl.rss.articles.xml",
            "category": "binnenland",
            "interval": 5,
        }
    """

    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "feed": {"type": "string"},
            "category": {"type": "string"},
            "interval": {"type": "integer"},
        },
        "required": ["name", "feed", "category"],
    }

    data = request.get_json(silent=True)
    if not data:
        return make_response_from_error(
            HTTPStatus.BAD_REQUEST,
            ErrorKind.InvalidJson,
        )

    try:
        validate(instance=data, schema=schema)
    except ValidationError as e:
        return make_response_from_error(
            HTTPStatus.BAD_REQUEST, ErrorKind.JsonValidationError, e.message
        )
    except SchemaError as e:
        print(f"jsonschema is invalid: {e.message}", file=sys.stderr)
        raise e

    db = await get_db()

    feed_name = data["name"].lower()
    feed_url = data["feed"]
    feed_category = data["category"].lower()
    feed_interval = data.get("interval", None)

    if not validate_url(feed_url):  # type: ignore
        return make_response_from_error(
            HTTPStatus.BAD_REQUEST, ErrorKind.InvalidFeedUrl, "Feed url is invalid"
        )

    # No idea why pyright thinks the type can be `Unknown`, but this "fixes" it.
    # TODO: Fixme
    url_components: ParseResult = urlparse(feed_url)  # type: ignore
    assert isinstance(url_components, ParseResult)

    news_source = url_components.netloc
    news_source_url = url_components.scheme + "://" + url_components.netloc

    try:
        # Update news-source with new rss entry if news-source already present,
        # else insert a new news-source with the rss feed.
        rss_create: RssEntriesCreateWithoutRelationsInput = {
            "name": feed_name,
            "feed": feed_url,
            "category": feed_category,
        }
        if feed_interval is not None:
            rss_create["interval"] = feed_interval

        await db.newssources.upsert(
            where={"name": news_source},
            data={
                "create": {
                    "name": news_source,
                    "url": news_source_url,
                    "rss": {"create": rss_create},
                },
                "update": {"rss": {"create": [rss_create]}},
            },
        )
    except UniqueViolationError as e:
        return make_response_from_error(
            HTTPStatus.BAD_REQUEST,
            ErrorKind.UniqueViolationError,
            str(e.with_traceback(None)),
        )
    except Exception as e:
        print(e.with_traceback(None), file=sys.stderr)
        return make_response_from_error(
            HTTPStatus.INTERNAL_SERVER_ERROR,
            ErrorKind.ServerError,
        )

    await db.flags.upsert(
        where={"name": "rss_feeds_modified"},
        data={
            "create": {"name": "rss_feeds_modified", "value": True},
            "update": {"value": True},
        },
    )

    return make_success_response()


@rss_bp.delete("/")
async def delete_rss() -> Response:
    """data": {},
    Delete rss feeds from the database

    # Feed json structure: (checked using schema validation)

    .. code-block:: json

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
            }
        },
        "required": ["feeds"],
    }

    data = request.get_json(silent=True)
    if not data:
        return make_response_from_error(
            HTTPStatus.BAD_REQUEST,
            ErrorKind.InvalidJson,
        )

    try:
        validate(instance=data, schema=schema)
    except ValidationError as e:
        return make_response_from_error(
            HTTPStatus.BAD_REQUEST,
            ErrorKind.JsonValidationError,
            e.message,
        )
    except SchemaError as e:
        print(f"jsonschema is invalid: {e.message}", file=sys.stderr)
        raise e

    db = await get_db()
    sources: set[int] = set()

    for feed in data["feeds"]:
        feed_entry = await db.rssentries.find_unique(
            where={"feed": feed}, include={"source": True}
        )
        if feed_entry is None:
            return make_response_from_error(
                HTTPStatus.BAD_REQUEST,
                ErrorKind.RecordNotFoundError,
            )
        if feed_entry.source is None:
            return make_response_from_error(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                ErrorKind.RecordNotFoundError,
            )

        sources.add(feed_entry.source.id)

    b = db.batch_()
    for feed in data["feeds"]:
        b.rssentries.delete(where={"feed": feed})
    try:
        await b.commit()
    except Exception as e:
        print(e.with_traceback(None), file=sys.stderr)
        return make_response_from_error(
            HTTPStatus.INTERNAL_SERVER_ERROR,
            ErrorKind.ServerError,
        )

    for source in sources:
        source_entry = await db.newssources.find_unique(
            where={"id": source}, include={"rss": True}
        )
        if source_entry is None:
            return make_response_from_error(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                ErrorKind.RecordNotFoundError,
                "",
            )
        if not source_entry.rss:
            await db.newssources.delete(where={"id": source})

    await db.flags.upsert(
        where={"name": "rss_feeds_modified"},
        data={
            "create": {"name": "rss_feeds_modified", "value": True},
            "update": {"value": True},
        },
    )

    return make_success_response()
