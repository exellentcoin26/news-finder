from flask import Blueprint, Response, make_response, jsonify, request
from http import HTTPStatus
from typing import List, Dict
import sys

from news_finder.db import get_db
from news_finder.utils.error_response import make_error_response, ResponseError

article_bp = Blueprint("article", __name__, url_prefix="/article")


@article_bp.get("/")
async def get_articles() -> Response:
    """
    Get a json with all the articles and their news source. set the `amount` and
    `offset` parameters to specify a range of articles to retrieve.

    # Articles json structure:
    {
        "articles": [
            {
                "source": "www.vrt.be",
                "article": {
                    "title": "Is the cat still there?",
                    "description": "The most interesting article about a cat in a tree."
                    "photo": "https://www.test-photo.io",
                    "link": "https:foo.article/article1.html"
                }
            },
            {
                "source": "www.vrt.be",
                "article": {
                    "title": "Is the cat already there?",
                    "description": "The most interesting article about a cat on its way home."
                    "photo": null
                    "link": "https:foo.article/article2.html"
            },
            ...
        ]
    }
    """

    try:
        amount = int(request.args.get("amount") or 50)
        offset = int(request.args.get("offset") or 0)
    except ValueError:
        return make_error_response(
            ResponseError.IncorrectParameters,
            "Parameters to get request are not integer values",
            HTTPStatus.BAD_REQUEST,
        )

    db = await get_db()

    try:
        articles = await db.newsarticles.find_many(
            take=amount,
            skip=offset,
            include={"source": True},
            # hardcode order for now
            # TODO: Remove this hardcode
            order={"publication_date": "desc"},
        )
    except Exception as e:
        print(e.with_traceback(None), file=sys.stderr)
        return make_error_response(
            ResponseError.ServerError, "", HTTPStatus.INTERNAL_SERVER_ERROR
        )

    response: Dict[str, List[Dict[str, str | Dict[str, str | None]]]] = {"articles": []}
    for article in articles:
        assert (
            article.source is not None
        ), "article should always have a source associated with it"

        news_source = article.source.name

        response["articles"].append(
            {
                "source": news_source,
                "article": {
                    "title": article.title,
                    "description": article.description,
                    "photo": article.photo,
                    "link": article.url,
                },
            }
        )

    return make_response(jsonify(response), HTTPStatus.OK)
