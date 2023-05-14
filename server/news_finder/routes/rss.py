from flask import Blueprint, Response, request
from urllib.parse import ParseResult, urlparse
from http import HTTPStatus
from jsonschema import SchemaError, validate, ValidationError
from prisma.errors import UniqueViolationError
from typing import Dict, List, Tuple

from prisma.models import RssEntries

from news_finder.db import get_db
from news_finder.response import (
    make_response_from_error,
    ErrorKind,
    make_success_response,
)

import sys

rss_bp = Blueprint("rss", __name__, url_prefix="/rss")


def parse_url(feed_url: str) -> Tuple[str, str]:
    # No idea why pyright thinks the type can be `Unknown`, but this "fixes" it.
    # TODO: Fixme
    url_components: ParseResult = urlparse(feed_url)  # pyright: ignore
    assert isinstance(url_components, ParseResult)

    news_source = url_components.netloc
    news_source_url = url_components.scheme + "://" + url_components.netloc

    return news_source, news_source_url


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
            "feeds": [
                {
                    "name": "VRT Wereld nieuws",
                    "feed": "https://www.vrt.be/vrtnws/nl.rss.articles.xml",
                },
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
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "feed": {"type": "string"},
                    },
                    "required": ["name", "feed"],
                },
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
            HTTPStatus.BAD_REQUEST, ErrorKind.JsonValidationError, e.message
        )
    except SchemaError as e:
        print(f"jsonschema is invalid: {e.message}", file=sys.stderr)
        raise e

    db = await get_db()
    b = db.batch_()

    feeds = data["feeds"]
    for rss_feed in feeds:
        feed_name = rss_feed["name"]
        feed_url = rss_feed["feed"]

        if (
            len(feeds) > 1
            and await db.rssentries.find_first(where={"feed": feed_url}) is not None
        ):
            # ignore duplicates if batch insert is done
            continue

        # No idea why pyright thinks the type can be `Unknown`, but this "fixes" it.
        # TODO: Fixme
        url_components: ParseResult = urlparse(feed_url)  # pyright: ignore
        assert isinstance(url_components, ParseResult)

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
                    "rss": {"create": {"name": feed_name, "feed": feed_url}},
                },
                "update": {"rss": {"create": [{"name": feed_name, "feed": feed_url}]}},
            },
        )

    try:
        await b.commit()
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

    return make_success_response()
