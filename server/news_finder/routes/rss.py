from flask import Blueprint, Response, request
from urllib.parse import ParseResult, urlparse
from jsonschema import SchemaError, validate, ValidationError

from news_finder.db import get_db

rss_bp = Blueprint("rss", __name__, url_prefix="/rss")


schema = {
    "type": "object",
    "properties": {
        "feeds": {
            "description": "list off rss feeds to be added",
            "type": "array",
            "items": {
                "type": "string"
            }
        },
    },
    "required": ["feeds"]
}


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

    # TODO: Check for success and handle accordingly
    data = request.get_json(silent=True)
    if not data:
        return Response({"error": "invalid json"}, status=400)

    try:
        validate(instance=data, schema=schema)
    except ValidationError as e:
        return Response(
            {"error": "json schema validation failed", "message": e.message},
            status=400
        )
    except SchemaError as e:
        print("jsonschema is invalid: ", e.message)
        raise e

    db = await get_db()

    b = db.batch_()

    for rss_feed in data["feeds"]:
        # extract news source and news source url from rss feed url
        url_components: ParseResult = urlparse(rss_feed)

        news_source = url_components.netloc
        news_source_url = url_components.scheme + url_components.netloc

        b.newssources.upsert(
            where={
                "name": news_source
            },
            data={
                "create": {
                    "name": news_source,
                    "url": news_source_url,
                    "rss": {
                        "create": {
                            "feed": rss_feed
                        }
                    }
                },
                "update": {
                    "rss": {
                        "create": [{
                            "feed": rss_feed,
                        }]
                    }
                }

            }
        )

    try:
        await b.commit()
    except Exception as e:
        print(e.with_traceback(None))
        return Response(status=500)

    return Response(status=200)
