from flask import Blueprint, Response, request

from http import HTTPStatus
from typing import List, Dict, Literal, Any
from dataclasses import dataclass

import sys
import traceback

from prisma.models import NewsArticles
from prisma.types import (
    NewsArticlesInclude,
    NewsArticlesOrderByInput,
    NewsArticlesWhereInput,
)

from news_finder.db import get_db
from news_finder.response import (
    make_response_from_error,
    ErrorKind,
    make_success_response,
)

article_bp = Blueprint("article", __name__, url_prefix="/article")


@dataclass
class NewsArticlesFindParams:
    take: int
    skip: int
    include: NewsArticlesInclude
    where: NewsArticlesWhereInput | None
    order: List[NewsArticlesOrderByInput]

    def add_where(self, where: NewsArticlesWhereInput, relation: Literal["OR", "AND"]):
        if self.where is None:
            self.where = where
        else:
            # Create a filter from both conditions using the provided relation
            self.where = NewsArticlesWhereInput(**{relation: [self.where, where]})


def remove_updated(articles: List[NewsArticles]) -> List[NewsArticles]:
    result: List[NewsArticles] = []

    for article in articles:
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

            if (
                article.publication_date is not None
                and similar_article_sources.get(article.source_id, 0)
                > article.publication_date.timestamp()
            ):
                continue

        result.append(article)

    return result


@article_bp.get("/")
async def get_articles() -> Response:
    """
    Get a json with all the articles and their news source.

    Articles are ordened by recency and versions that have an upadate are emitted.

    # Parameters:
        - amount: Amount of articles to retrieve.
        - offset: Offset in the article selection list.
        - label: Filter for the articles to retrieve.
        - sortBy:
            * recency (default)
            * popularity

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
        category = request.args.get("label") or None
        sort_by = request.args.get("sortBy") or "recency"

        if sort_by not in ("recency", "popularity"):
            raise ValueError(f"sortBy has invalid value `{sort_by}`")
    except ValueError as e:
        return make_response_from_error(
            HTTPStatus.BAD_REQUEST,
            ErrorKind.IncorrectParameters,
            str(e),
        )

    db = await get_db()

    article_find_params = NewsArticlesFindParams(
        take=amount,
        skip=offset,
        include=NewsArticlesInclude(
            {
                "source": True,
                "similar_articles": {
                    "include": {"similar": {"include": {"source": True}}}
                },
            }
        ),
        where=None,
        order=[],
    )

    match sort_by:
        case "recency":
            article_find_params.order.append({"publication_date": "desc"})
        case "popularity":
            # Group all history entries by article id when they are not NULL. Count the
            # entries per group and return the appropriate amount with a descending
            # count.

            popular_articles = await db.query_raw(
                f""" 
                SELECT article_id, COUNT(*) as count
                FROM "UserArticleHistory"
                WHERE article_id IS NOT NULL
                GROUP BY article_id
                ORDER BY count DESC
                OFFSET {offset}
                LIMIT {amount}
                """  # type: ignore
            )
            popular_article_ids = [
                popular_article["article_id"] for popular_article in popular_articles
            ]

            article_find_params.add_where({"id": {"in": popular_article_ids}}, "AND")

    if category is not None:
        article_find_params.add_where(
            {"labels": {"some": {"label": {"contains": category}}}}, "AND"
        )

    try:
        articles = await db.newsarticles.find_many(**vars(article_find_params))
    except Exception:
        traceback.print_exc(file=sys.stderr)
        return make_response_from_error(
            HTTPStatus.INTERNAL_SERVER_ERROR,
            ErrorKind.ServerError,
        )

    # Remove older version of article that has newer entry in list.
    articles = remove_updated(articles)

    response: Dict[str, List[Dict[str, str | Dict[str, str | float | None]]]] = {
        "articles": []
    }

    if sort_by == "popularity":
        articles.sort(key=lambda article: popular_article_ids.index(article.id))

    for article in articles:
        assert (
            article.source is not None
        ), "article should always have a source associated with it"

        news_source = article.source.name
        # TODO: Define set of response objects with TypedDict.
        entry: Dict[str, Any] = {
            "source": news_source,
            "article": {
                "title": article.title,
                "description": article.description,
                "photo": article.photo,
                "link": article.url,
            },
        }

        if article.publication_date is not None:
            entry["article"]["publication_date"] = article.publication_date.timestamp()

        response["articles"].append(entry)

    return make_success_response(HTTPStatus.OK, response)


@article_bp.get("/similar/")
async def get_similar_articles() -> Response:
    article_link = str(request.args.get("url"))

    db = await get_db()

    try:
        current_article = await db.newsarticles.find_unique(
            where={
                "url": article_link,
            },
        )

        assert current_article is not None, "article should always exist in database"

        assert current_article.id is not None, "article should always have an id"

        similar_articles = await db.similararticles.find_many(
            where={
                "id1": current_article.id,
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
            pair.id1 is not None
        ), "article in similar articles table should always have an id"

        assert (
            pair.id2 is not None
        ), "article in similar articles table should always have a similar article associated with it with an id"

        similar_article = await db.newsarticles.find_unique(
            where={
                "id": pair.id2,
            },
            include={"source": True},
        )

        assert (
            similar_article is not None
        ), "similar article should always exist in the database"

        assert (
            similar_article.source is not None
        ), "an article should always have a source associated with it"

        response["articles"].append(
            {"source": similar_article.source.name, "link": similar_article.url}
        )

    return make_success_response(HTTPStatus.OK, response)
