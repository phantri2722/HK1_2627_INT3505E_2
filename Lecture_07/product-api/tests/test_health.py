from unittest.mock import patch

from sqlalchemy.exc import OperationalError


# -----------------------------------------
# Test liveness
# -----------------------------------------

def test_health_check(client):
    response = client.get("/healthz")

    assert response.status_code == 200

    assert response.get_json() == {
        "status": "alive"
    }


# -----------------------------------------
# Test readiness: database available
# -----------------------------------------

def test_readiness_check(client):
    response = client.get("/ready")

    assert response.status_code == 200

    assert response.get_json() == {
        "status": "ready",
        "database": "connected"
    }


# -----------------------------------------
# Test readiness: database unavailable
# -----------------------------------------

def test_readiness_database_failure(client):
    error = OperationalError(
        "SELECT 1",
        {},
        Exception("Database connection failed")
    )

    with patch(
        "routes.health.db.session.execute",
        side_effect=error
    ):
        response = client.get("/ready")

    assert response.status_code == 503

    assert response.get_json() == {
        "status": "not_ready",
        "database": "unavailable"
    }