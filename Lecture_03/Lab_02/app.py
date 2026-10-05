from flask import Flask, jsonify

from errors import ProblemError, register_error_handlers


app = Flask(__name__)

register_error_handlers(app)


USERS = {
    1: {
        "id": 1,
        "name": "Alice"
    },
    2: {
        "id": 2,
        "name": "Bob"
    }
}


@app.get("/users/<int:user_id>")
def get_user(user_id):

    user = USERS.get(user_id)

    if user is None:
        raise ProblemError(
            status=404,
            title="User not found",
            detail=f"User with id {user_id} does not exist.",
            type_uri="https://api.example.com/problems/user-not-found",
            resource_id=user_id
        )

    return jsonify(user), 200


@app.get("/error")
def test_internal_error():
    # deliberately generate an unexpected error
    x = 1 / 0

    return {"value": x}


if __name__ == "__main__":
    app.run(debug=True)