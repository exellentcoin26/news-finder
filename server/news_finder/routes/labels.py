# from prisma import Prisma
from flask import Blueprint
from http import HTTPStatus
from news_finder.db import get_db
from news_finder.response import make_success_response


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

    feeds = await db.rssentries.find_many()

    for feed in feeds:
        labels.add(feed.category)
            
    response: dict[str, list[str]] = {"labels": []}
    for label in labels:
        response["labels"].append(label)

    return make_success_response(HTTPStatus.OK, response)
