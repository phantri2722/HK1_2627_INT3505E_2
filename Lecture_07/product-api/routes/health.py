from flask import Blueprint, jsonify
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from extensions import db


health_bp = Blueprint("health", __name__)


# -----------------------------------------
# GET /healthz — Liveness
# -----------------------------------------

@health_bp.get("/healthz")
def health_check():
    return jsonify({
        "status": "alive"
    }), 200


# -----------------------------------------
# GET /ready — Readiness
# -----------------------------------------

@health_bp.get("/ready")
def readiness_check():
    try:
        db.session.execute(text("SELECT 1"))

        return jsonify({
            "status": "ready",
            "database": "connected"
        }), 200

    except SQLAlchemyError:
        db.session.rollback()

        return jsonify({
            "status": "not_ready",
            "database": "unavailable"
        }), 503