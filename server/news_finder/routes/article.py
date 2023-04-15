from flask import Blueprint, Response, make_response, jsonify
from http import HTTPStatus
from typing import List, Dict
import sys

from news_finder.db import get_db
from news_finder.utils.error_response import make_error_response, ResponseError

article_bp = Blueprint("article", __name__, url_prefix="/article")


@article_bp.get("/")
async def get_articles() -> Response:
    """
    Get a json with all the articles and their news source
    # Articles json structure:
    {
        "articles": [
            {
                "source": "www.vrt.be",
                "article": {
                    "title": "Is the cat still there?",
                    "description": "The most interesting article about a cat in a tree."
                    "photo": "https://www.test-photo.io"
                }
            },
            {
                "source": "www.vrt.be",
                "article": {
                    "title": "Is the cat already there?",
                    "description": "The most interesting article about a cat on its way home."
                    "photo": null
            },
            ...
        ]
    }
    """

    db = await get_db()

    try:
        articles = await db.newsarticles.find_many(include={"source": True})
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
                },
            }
        )

    return make_response(jsonify(response), HTTPStatus.OK)
