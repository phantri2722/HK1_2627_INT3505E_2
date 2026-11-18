from flask import Blueprint

from .users_data import get_user

bp = Blueprint("v2", __name__)


@bp.get("/users/<int:user_id>")
def read_user(user_id):
    user = get_user(user_id)
    if user is None:
        return {"error": "User not found"}, 404

    return {
        "id": user_id,
        "first_name": user["first_name"],
        "last_name": user["last_name"],
        "email": user["email"],
    }