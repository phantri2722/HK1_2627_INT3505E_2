"""LAB 1 — add your five tests here. Do not delete the smoke tests.

A. GET /books, empty database -> HTTP 200 and []
B. GET /books/9999 -> HTTP 404, JSON code == NOT_FOUND
C. POST /books with only author -> HTTP 400, errors contains title
D. POST valid book, DELETE it, GET same id -> HTTP 404
BONUS. Validate a Book response using JSON Schema; add an unknown
       field to a *copy* of the response and assert ValidationError.

Useful imports:
    from jsonschema import validate, ValidationError
    import pytest
    from tools import get_book_schema

Do not depend on test execution order. Fixtures: client, app, sample_book.
"""
import pytest
from jsonschema import ValidationError, validate

# Test A: GET /books when the database is empty must return empty array (not null)
def test_list_books_empty(client):
    response = client.get("/books")
    assert response.status_code == 200
    assert response.is_json
    assert response.get_json() == []

# Test B: GET /books/id with non-existed id returns 404 + "code":"NOT_FOUND"
def test_get_nonexisted_book(client):
    response = client.get("/books/22012005")

    assert response.status_code == 404
    assert response.get_json()["code"] == "NOT_FOUND"

# Test C: POST /books without title retuns 400 + field "title" included in errors
def test_create_book_without_title(client):
    response = client.post("/books", json={"author": "Alice"})

    assert response.status_code == 400

    body = response.get_json()
    assert body["code"] == "VALIDATION_ERROR"
    assert "title" in {error["field"] for error in body["errors"]}

# Test D: DELETE /books/id and GET /books/id with the same id returns 404
def test_get_the_same_book_deleted(client):
    created = client.post(
        "/books",
        json={"title": "Test Book", "author": "Alice"},
    )
    assert created.status_code == 201
    book_id = created.get_json()["id"]

    deleted = client.delete(f"/books/{book_id}")
    assert deleted.status_code == 204
    assert deleted.data == b""

    getting = client.get(f"/books/{book_id}")
    assert getting.status_code == 404
    assert getting.get_json()["code"] == "NOT_FOUND"

# Bonus test: A response schema must reject unexpected fields such password_hash
def test_response_extra_field_blocked(client, sample_book):
    schema = {
        "type": "object",
        "required": ["id", "title", "author", "year", "isbn"],
        "additionalProperties": False,
        "properties": {
            "id": {"type": "integer", "minimum": 1},
            "title": {"type": "string", "minLength": 1, "maxLength": 200},
            "author": {"type": "string", "minLength": 1, "maxLength": 200},
            "year": {
                "type": ["integer", "null"],
                "minimum": 1450,
                "maximum": 2100,
            },
            "isbn": {
                "type": ["string", "null"],
                "pattern": r"^\d{13}$",
            },
        },
    }

    response = client.get(f"/books/{sample_book}")
    assert response.status_code == 200
    body = response.get_json()

    validate(instance=body, schema=schema)
    leaked_body = {**body, "password_hash":"fake-secret"}

    with pytest.raises(ValidationError):
        validate(instance=leaked_body, schema=schema)