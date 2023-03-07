from flask import Response, Blueprint, make_response, jsonify

root_bp = Blueprint("root", __name__, url_prefix="/")


# route for docker to check whether the server is up and running
@root_bp.get("/healthcheck")
def healthcheck() -> Response:
    return make_response(
        jsonify({"message": "the server is up and running", "status": 200}),
        200
    )
