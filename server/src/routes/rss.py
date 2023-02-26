from flask import Blueprint, Response, request, abort
from urllib.parse import urlparse
from jsonschema import validate

rss_bp = Blueprint("rss", __name__, url_prefix="/rss")


@rss_bp.post("/")
def add_rss_feed() -> Response:
    """
    # Feed json structure: (checked usign schema validation)
    {
        "feeds": [
            {
                "news-source": "Vrt Nieuws"
                "rss": "https://www.vrt.be/vrtnws/nl.rss.articles.xml"
            },
            {
                ...
            },
            ...
        ]
    }
    """
    # TODO: Check for success and handle accordingly
    data = request.get_json()

    return Response()
