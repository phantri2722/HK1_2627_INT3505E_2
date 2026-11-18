from functools import wraps

from flask import Flask, jsonify, make_response, request

app = Flask(__name__)

DEFAULT_VERSION = "2"
SUPPORTED_VERSIONS = {"1", "2", "2024-06-20"}

USERS = {
    1: {"first_name": "Văn", "last_name": "Nguyễn", "email": "a@vnu.vn"},
}


def api_version(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        version = request.headers.get("X-API-Version", DEFAULT_VERSION)

        if version not in SUPPORTED_VERSIONS:
            return jsonify(error="Unsupported API version"), 400

        response = make_response(view(*args, version=version, **kwargs))
        response.headers["X-API-Version-Served"] = version
        response.vary.add("X-API-Version")
        return response

    return wrapper


@app.get("/users/<int:user_id>")
@api_version
def read_user(user_id, version):
    user = USERS.get(user_id)
    if user is None:
        return {"error": "User not found"}, 404

    if version == "1":
        return {
            "id": user_id,
            "full_name": f"{user['first_name']} {user['last_name']}",
        }

    return {"id": user_id, **user}


if __name__ == "__main__":
    app.run(port=5000)