from flask import Blueprint, Response, request
from http import HTTPStatus
from jsonschema import SchemaError, validate, ValidationError
import sys

from news_finder.db import get_db
from news_finder.response import (
    make_response_from_error,
    ErrorKind,
    make_success_response,
)


history_bp = Blueprint("user", __name__, url_prefix="/user-history")

@history_bp.post("/")

async def store_user_history() -> Response:    
        """
        # Json structure: Username of user that is currently logged in and the article on which he clicked

        .. code-block:: json

            {
                "username": "name",
                "article": {
                            "title": "Is the cat still there?",
                            "description": "The most interesting article about a cat in a tree."
                            "photo": "https://www.test-photo.io",
                            "link": "https:foo.article/article1.html"
                        }
            }
        """

        schema = {
            "type": "object",
            "properties": {
                 "username" : {
                      "description": "Name of the user that is currently logged in",
                      "type": "string",     
                 },
                "article": {
                     "description": "Article on which the user clicked",
                     "type": "object",
                     "items": {"type":"string"},
                }
            },
            "required": "username"
        }

        data = request.get_json(silent=True)
        if not data:
            return make_response_from_error(HTTPStatus.BAD_REQUEST, ErrorKind.InvalidJson)

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

        user = await db.users.find_first(where={"username": data["username"]})
        if user is not None:
            clicked_article = await db.newsarticles.find_first(where={"url": data["article"]["link"]})


            userarticle = b.usersarticles.create(
                data={
                        "user": user.username,
                        "user_id": user.id,
                        "url": clicked_article.url,
                        "source": clicked_article.source,
                        "source_id": clicked_article.source_id,
                        "article": clicked_article,
                        "article_id": clicked_article.id          
                }
            )
            
            user.History.append(userarticle)
            return make_success_response()












