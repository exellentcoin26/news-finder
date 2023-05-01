# from prisma import Prisma
from flask import Blueprint
from http import HTTPStatus
from news_finder.db import get_db
from news_finder.response import (
    make_response_from_error,
    ErrorKind,
    make_success_response,
)


labels_bp = Blueprint("labels", __name__, url_prefix="/labels")


@labels_bp.get("/")
async def get_labels():
    """
    Get a json with all the possible labels
    
    # Labels json structure:
    
    .. code-block:: json
        
        {
            "labels": [
                "binnenland",
                "buitenland",
                "economie",
                ...
            ]
        }
    """
    
    labels: set[str] = set()
    db = await get_db()

    articles = await db.newsarticles.find_many(include={"labels": True})

    for article in articles:
        if article.labels is None:
            return make_response_from_error(HTTPStatus.INTERNAL_SERVER_ERROR, ErrorKind.ServerError)
        for label in article.labels:
            labels.add(label.label)
            
    response: dict[str, list[str]] = {"labels": []}
    for label in labels:
        response["labels"].append(label)

    return make_success_response(HTTPStatus.OK, response)
