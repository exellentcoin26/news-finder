from flask import Blueprint, Response, request

from http import HTTPStatus
from typing import List, Dict

import sys

from news_finder.db import get_db
from news_finder.response import (
    make_response_from_error,
    ErrorKind,
    make_success_response,
)

article_bp = Blueprint("article", __name__, url_prefix="/article")


@article_bp.get("/")
async def get_articles() -> Response:
    """
    Get a json with all the articles and their news source. set the `amount` and
    `offset` parameters to specify a range of articles to retrieve.

    Articles are ordened by recency and versions that have an upadate are emitted.

    # Articles json structure:

    .. code-block:: json

        {
            "articles": [
                {
                    "source": "www.vrt.be",
                    "article": {
                        "title": "Is the cat still there?",
                        "description": "The most interesting article about a cat in a tree."
                        "photo": "https://www.test-photo.io",
                        "link": "https:foo.article/article1.html"
                        "publication_date": 2021-09-27 15:22:00
                    }
                },
                {
                    "source": "www.vrt.be",
                    "article": {
                        "title": "Is the cat already there?",
                        "description": "The most interesting article about a cat on its way home."
                        "photo": null
                        "link": "https:foo.article/article2.html"
                        "publication_date": 2021-09-30 08:16:00
                },
                ...
            ]
        }
    """

    try:
        amount = int(request.args.get("amount") or 50)
        offset = int(request.args.get("offset") or 0)
        category = request.args.get("label") or ""
    except ValueError:
        return make_response_from_error(
            HTTPStatus.BAD_REQUEST,
            ErrorKind.IncorrectParameters,
            "Parameters to get request are not integer values",
        )

    db = await get_db()

    if category == "":
        try:
            articles = await db.newsarticles.find_many(
                take=amount,
                skip=offset,
                include={
                    "source": True,
                    "similar_articles": {
                        "include": {"similar": {"include": {"source": True}}}
                    },
                },
                # hardcode order for now
                # TODO: Remove this hardcode
                order={"publication_date": "desc"},
            )
        except Exception as e:
            print(e.with_traceback(None), file=sys.stderr)
            return make_response_from_error(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                ErrorKind.ServerError,
            )
    else:
        try:
            articles = await db.newsarticles.find_many(
                take=amount,
                skip=offset,
                where={
                    "labels": {
                        "some": {
                            "label": {"contains": category}
                        }
                    }
                },
                include={
                    "source": True,
                    "similar_articles": {
                        "include": {"similar": {"include": {"source": True}}}
                    },
                },
                # hardcode order for now
                # TODO: Remove this hardcode
                order={"publication_date": "desc"},
            )
        except Exception as e:
            print(e.with_traceback(None), file=sys.stderr)
            return make_response_from_error(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                ErrorKind.ServerError,
            )

    response: Dict[str, List[Dict[str, str | Dict[str, str | float | None]]]] = {"articles": []}
    for article in articles:
        assert (
            article.source is not None
        ), "article should always have a source associated with it"

        # Remove old versions that have been updated
        if article.similar_articles is not None:
            # article id -> datatime timestamp
            similar_article_sources: Dict[int, float] = {}

            for sim in article.similar_articles:
                assert (
                    sim.similar is not None
                ), "similar for similar articles cannot be none"
                assert (
                    sim.similar.source is not None
                ), "similar.similar_source for similar article cannot be none"

                if sim.similar.publication_date is None:
                    continue

                similar_article_sources[sim.similar.source.id] = max(
                    similar_article_sources.get(sim.similar.source_id, 0),
                    sim.similar.publication_date.timestamp(),
                )

            if article.publication_date is not None:
                if (
                    similar_article_sources.get(article.source_id, 0)
                    > article.publication_date.timestamp()
                ):
                    continue

        assert (
                article.publication_date is not None
        ), "article should always have a publication date"

        news_source = article.source.name

        response["articles"].append(
            {
                "source": news_source,
                "article": {
                    "title": article.title,
                    "description": article.description,
                    "photo": article.photo,
                    "link": article.url,
                    "publication_date": article.publication_date.timestamp(),
                },
            }
        )

    return make_success_response(HTTPStatus.OK, response)

@article_bp.get("/similar/")
async def get_similar_articles() -> Response:

    article_link = str(request.args.get("url"))

    db = await get_db()

    try:
        current_article = await db.newsarticles.find_unique(
            where={
                "url":article_link,
            },
        )

        assert (
                current_article is not None
        ), "article should always exist in database"

        assert (
                current_article.id is not None
        ), "article should always have an id"

        similar_articles = await db.similararticles.find_many(
            where={
                "id1":current_article.id,
            }
        )
    except Exception as e:
        print(e.with_traceback(None), file=sys.stderr)
        return make_response_from_error(
            HTTPStatus.INTERNAL_SERVER_ERROR,
            ErrorKind.ServerError,
        )

    response: Dict[str, List[Dict[str, str]]] = {"articles": []}
    for pair in similar_articles:

        assert (
                pair.similar is not None and pair.similar.id is not None
        ), "article in similar articles table should always have a similar article associated with it"

        assert (
                pair.similar.id is not None
        ), "article in news articles table should always have an id"

        similar_article = await db.newsarticles.find_unique(
            where={
                "id":pair.similar.id,
            },
        )

        assert (
                similar_article is not None
        ), "article should always exist in database"

        assert (
                similar_article.source is not None
        ), "article should always have a source associated with it"

        response["articles"].append(
            {
                "source": similar_article.source.name,
                "link": similar_article.url
            }
        )


    return make_success_response(HTTPStatus.OK, response)