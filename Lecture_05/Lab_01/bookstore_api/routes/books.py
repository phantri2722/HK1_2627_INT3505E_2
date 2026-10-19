import json
from pathlib import Path

from flask import (
    Blueprint,
    jsonify,
    request
)

from jsonschema import (
    validate,
    ValidationError
)

from models import (
    db,
    Book,
    Author,
    Category
)


books_bp = Blueprint(
    "books",
    __name__,
    url_prefix="/api/v1/books"
)


# ============================================================
# Load JSON Schema once
# ============================================================

SCHEMA_PATH = (
    Path(__file__).parent.parent
    / "schemas"
    / "book.json"
)

with SCHEMA_PATH.open(
    "r",
    encoding="utf-8"
) as file:

    BOOK_SCHEMA = json.load(file)


# ============================================================
# GET /api/v1/books
# ============================================================

@books_bp.get("")
def list_books():

    books = Book.query.order_by(
        Book.id.asc()
    ).all()

    return jsonify([
        book.to_dict()
        for book in books
    ]), 200


# ============================================================
# GET /api/v1/books/{id}
# ============================================================

@books_bp.get("/<int:book_id>")
def get_book(book_id):

    book = db.session.get(
        Book,
        book_id
    )

    if book is None:
        return jsonify({
            "error": "book_not_found"
        }), 404

    return jsonify(
        book.to_dict()
    ), 200


# ============================================================
# POST /api/v1/books
# ============================================================

@books_bp.post("")
def create_book():

    payload = request.get_json(
        silent=True
    )

    if payload is None:
        return jsonify({
            "error": "invalid_json"
        }), 400

    # --------------------------------------------------------
    # JSON Schema validation
    # --------------------------------------------------------

    try:
        validate(
            instance=payload,
            schema=BOOK_SCHEMA
        )

    except ValidationError as error:

        return jsonify({
            "error": "validation_failed",
            "field": list(error.path),
            "message": error.message
        }), 400


    # --------------------------------------------------------
    # Check duplicate ISBN
    # --------------------------------------------------------

    existing_book = Book.query.filter_by(
        isbn=payload["isbn"]
    ).first()

    if existing_book is not None:
        return jsonify({
            "error": "isbn_exists"
        }), 409


    # --------------------------------------------------------
    # Find category
    # --------------------------------------------------------

    category = db.session.get(
        Category,
        payload["category_id"]
    )

    if category is None:
        return jsonify({
            "error": "category_not_found"
        }), 400


    # --------------------------------------------------------
    # Find authors
    # --------------------------------------------------------

    author_ids = payload.get(
        "author_ids",
        []
    )

    authors = []

    for author_id in author_ids:

        author = db.session.get(
            Author,
            author_id
        )

        if author is None:
            return jsonify({
                "error": "author_not_found",
                "author_id": author_id
            }), 400

        authors.append(author)


    # --------------------------------------------------------
    # Create Book
    # --------------------------------------------------------

    book = Book(
        title=payload["title"],
        isbn=payload["isbn"],
        price_vnd=payload["price_vnd"],
        stock=payload.get("stock", 0),
        category=category,
        authors=authors
    )

    db.session.add(book)
    db.session.commit()


    response = jsonify(
        book.to_dict()
    )

    response.status_code = 201
    response.headers["Location"] = (
        f"/api/v1/books/{book.id}"
    )

    return response


# ============================================================
# PATCH /api/v1/books/{id}
# ============================================================

@books_bp.patch("/<int:book_id>")
def update_book(book_id):

    book = db.session.get(
        Book,
        book_id
    )

    if book is None:
        return jsonify({
            "error": "book_not_found"
        }), 404


    payload = request.get_json(
        silent=True
    ) or {}


    # --------------------------------------------------------
    # Simple partial updates
    # --------------------------------------------------------

    if "title" in payload:

        title = str(
            payload["title"]
        ).strip()

        if not title:
            return jsonify({
                "error": "title_empty"
            }), 400

        book.title = title


    if "price_vnd" in payload:

        price = payload["price_vnd"]

        if (
            not isinstance(price, int)
            or price < 0
        ):
            return jsonify({
                "error": "invalid_price"
            }), 400

        book.price_vnd = price


    if "stock" in payload:

        stock = payload["stock"]

        if (
            not isinstance(stock, int)
            or stock < 0
        ):
            return jsonify({
                "error": "invalid_stock"
            }), 400

        book.stock = stock


    if "category_id" in payload:

        category = db.session.get(
            Category,
            payload["category_id"]
        )

        if category is None:
            return jsonify({
                "error": "category_not_found"
            }), 400

        book.category = category


    if "author_ids" in payload:

        authors = []

        for author_id in payload["author_ids"]:

            author = db.session.get(
                Author,
                author_id
            )

            if author is None:
                return jsonify({
                    "error": "author_not_found",
                    "author_id": author_id
                }), 400

            authors.append(author)

        book.authors = authors


    db.session.commit()

    return jsonify(
        book.to_dict()
    ), 200


# ============================================================
# DELETE /api/v1/books/{id}
# ============================================================

@books_bp.delete("/<int:book_id>")
def delete_book(book_id):

    book = db.session.get(
        Book,
        book_id
    )

    if book is None:
        return jsonify({
            "error": "book_not_found"
        }), 404


    db.session.delete(book)
    db.session.commit()

    return "", 204