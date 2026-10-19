import base64
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

from sqlalchemy import (
    select,
    func,
    and_,
    or_
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
# Configuration
# ============================================================

DEFAULT_LIMIT = 20
MAX_LIMIT = 100


# Public API sort names -> SQLAlchemy columns
SORT_FIELDS = {
    "id": Book.id,
    "title": Book.title,
    "price": Book.price_vnd,
    "stock": Book.stock
}


# ============================================================
# Load JSON Schema
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
# Cursor helpers
# ============================================================

def encode_cursor(state):
    """
    Python dict -> opaque Base64 URL-safe cursor.
    """

    raw = json.dumps(
        state,
        separators=(",", ":")
    ).encode("utf-8")

    return (
        base64
        .urlsafe_b64encode(raw)
        .decode("utf-8")
        .rstrip("=")
    )


def decode_cursor(token):
    """
    Opaque cursor -> Python dict.

    Raises ValueError when malformed.
    """

    try:
        padding = "=" * (-len(token) % 4)

        raw = base64.urlsafe_b64decode(
            token + padding
        )

        state = json.loads(
            raw.decode("utf-8")
        )

        if not isinstance(state, dict):
            raise ValueError()

        return state

    except Exception as exc:
        raise ValueError(
            "Invalid cursor"
        ) from exc


# ============================================================
# Multi-key sorting
# ============================================================

def parse_sort(raw_sort):
    """
    Example:
        -price,title

    becomes:
        price DESC,
        title ASC,
        id ASC

    id is automatically appended as a deterministic
    tie-breaker when it is not explicitly provided.
    """

    if not raw_sort:
        raw_sort = "-id"

    parts = [
        part.strip()
        for part in raw_sort.split(",")
        if part.strip()
    ]

    if not parts:
        raise ValueError(
            "sort must contain at least one field"
        )

    specs = []
    seen = set()

    for part in parts:

        descending = part.startswith("-")

        name = (
            part[1:]
            if descending
            else part
        )

        if name not in SORT_FIELDS:
            raise ValueError(
                f"Unsupported sort field: {name}"
            )

        if name in seen:
            raise ValueError(
                f"Duplicate sort field: {name}"
            )

        seen.add(name)

        specs.append({
            "name": name,
            "column": SORT_FIELDS[name],
            "descending": descending
        })


    # Cursor needs deterministic ordering.
    # Add the unique primary key as a tie-breaker.
    if "id" not in seen:

        specs.append({
            "name": "id",
            "column": Book.id,
            "descending": False
        })


    return raw_sort, specs


def order_expressions(specs):

    expressions = []

    for spec in specs:

        column = spec["column"]

        if spec["descending"]:
            expressions.append(
                column.desc()
            )
        else:
            expressions.append(
                column.asc()
            )

    return expressions


# ============================================================
# Generic lexicographic cursor condition
# ============================================================

def build_cursor_condition(
    specs,
    values
):

    if len(specs) != len(values):
        raise ValueError(
            "Cursor does not match sort definition"
        )

    clauses = []
    equals_prefix = []

    for spec, value in zip(
        specs,
        values
    ):

        column = spec["column"]

        if spec["descending"]:
            comparison = column < value
        else:
            comparison = column > value


        if equals_prefix:

            clauses.append(
                and_(
                    *equals_prefix,
                    comparison
                )
            )

        else:
            clauses.append(
                comparison
            )


        equals_prefix.append(
            column == value
        )


    return or_(*clauses)


# ============================================================
# Extract cursor values from final row
# ============================================================

def cursor_values(book, specs):

    values = []

    for spec in specs:

        name = spec["name"]

        if name == "price":
            value = book.price_vnd

        else:
            value = getattr(
                book,
                name
            )

        values.append(value)

    return values


# ============================================================
# GET /api/v1/books
#
# ============================================================

@books_bp.get("")
def list_books():

    # --------------------------------------------------------
    # Common parameters
    # --------------------------------------------------------

    strategy = request.args.get(
        "strategy",
        "cursor"
    )

    if strategy not in {
        "offset",
        "cursor"
    }:

        return jsonify({
            "error": "invalid_strategy",
            "message":
                "strategy must be offset or cursor"
        }), 400


    limit = request.args.get(
        "limit",
        DEFAULT_LIMIT,
        type=int
    )

    if (
        limit is None
        or limit < 1
        or limit > MAX_LIMIT
    ):

        return jsonify({
            "error": "invalid_limit",
            "message":
                f"limit must be between 1 and {MAX_LIMIT}"
        }), 400


    genre = request.args.get(
        "genre"
    )


    # --------------------------------------------------------
    # Multi-key sorting
    # --------------------------------------------------------

    sort_raw = request.args.get(
        "sort",
        "-id"
    )

    try:
        normalized_sort, specs = (
            parse_sort(sort_raw)
        )

    except ValueError as error:

        return jsonify({
            "error": "invalid_sort",
            "message": str(error)
        }), 400


    order_by = order_expressions(
        specs
    )


    # --------------------------------------------------------
    # Base query
    # --------------------------------------------------------

    query = select(Book)


    # Homework calls the filter "genre".
    # Our Lab 1 data model calls it Category.
    #
    # ?genre=tech
    # ->
    # Category.slug == "tech"
    # --------------------------------------------------------

    if genre:

        query = (
            query
            .join(Book.category)
            .where(
                Category.slug == genre
            )
        )


    query = query.order_by(
        *order_by
    )


    # ========================================================
    # OFFSET PAGINATION
    # ========================================================

    if strategy == "offset":

        if request.args.get("cursor"):
            return jsonify({
                "error": "invalid_parameters",
                "message":
                    "cursor cannot be used with offset strategy"
            }), 400


        offset = request.args.get(
            "offset",
            0,
            type=int
        )

        if (
            offset is None
            or offset < 0
        ):

            return jsonify({
                "error": "invalid_offset",
                "message":
                    "offset must be >= 0"
            }), 400


        # -----------------------------------------------
        # Count after filter
        # -----------------------------------------------

        count_query = select(
            func.count(Book.id)
        )

        if genre:

            count_query = (
                count_query
                .join(Book.category)
                .where(
                    Category.slug
                    == genre
                )
            )


        total = db.session.scalar(
            count_query
        )


        rows = db.session.scalars(
            query
            .offset(offset)
            .limit(limit)
        ).all()


        return jsonify({
            "data": [
                book.to_dict()
                for book in rows
            ],

            "pagination": {
                "strategy": "offset",
                "offset": offset,
                "limit": limit,
                "total": total,
                "has_more":
                    offset + len(rows)
                    < total
            },

            "sort": normalized_sort,
            "genre": genre
        }), 200


    # ========================================================
    # CURSOR PAGINATION
    # ========================================================

    if request.args.get("offset"):

        return jsonify({
            "error": "invalid_parameters",
            "message":
                "offset cannot be used with cursor strategy"
        }), 400


    cursor = request.args.get(
        "cursor"
    )


    if cursor:

        try:
            state = decode_cursor(
                cursor
            )

        except ValueError:

            return jsonify({
                "error": "invalid_cursor"
            }), 400


        # -----------------------------------------------
        # Bind cursor to the same sorting/filter state.
        #
        # If client changes sort or genre while reusing
        # the old cursor, reject it.
        # -----------------------------------------------

        if (
            state.get("sort")
            != normalized_sort
        ):

            return jsonify({
                "error": "cursor_sort_mismatch",
                "message":
                    "cursor was generated for another sort order"
            }), 400


        if (
            state.get("genre")
            != genre
        ):

            return jsonify({
                "error": "cursor_filter_mismatch",
                "message":
                    "cursor was generated for another genre filter"
            }), 400


        values = state.get(
            "values"
        )

        if not isinstance(
            values,
            list
        ):

            return jsonify({
                "error": "invalid_cursor"
            }), 400


        try:

            condition = (
                build_cursor_condition(
                    specs,
                    values
                )
            )

        except ValueError:

            return jsonify({
                "error": "invalid_cursor"
            }), 400


        query = query.where(
            condition
        )


    # limit + 1:
    # fetch one extra item to determine has_more.
    rows = db.session.scalars(
        query.limit(
            limit + 1
        )
    ).all()


    has_more = (
        len(rows) > limit
    )

    items = rows[:limit]


    next_cursor = None

    if items and has_more:

        last = items[-1]

        next_cursor = encode_cursor({
            "sort":
                normalized_sort,

            "genre":
                genre,

            "values":
                cursor_values(
                    last,
                    specs
                )
        })


    return jsonify({
        "data": [
            book.to_dict()
            for book in items
        ],

        "pagination": {
            "strategy": "cursor",
            "limit": limit,
            "next_cursor":
                next_cursor,
            "has_more":
                has_more
        },

        "sort": normalized_sort,
        "genre": genre
    }), 200


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
# POST
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


    try:

        validate(
            instance=payload,
            schema=BOOK_SCHEMA
        )

    except ValidationError as error:

        return jsonify({
            "error":
                "validation_failed",

            "field":
                list(error.path),

            "message":
                error.message
        }), 400


    existing_book = (
        Book.query
        .filter_by(
            isbn=payload["isbn"]
        )
        .first()
    )


    if existing_book:

        return jsonify({
            "error": "isbn_exists"
        }), 409


    category = db.session.get(
        Category,
        payload["category_id"]
    )

    if category is None:

        return jsonify({
            "error":
                "category_not_found"
        }), 400


    authors = []

    for author_id in payload.get(
        "author_ids",
        []
    ):

        author = db.session.get(
            Author,
            author_id
        )

        if author is None:

            return jsonify({
                "error":
                    "author_not_found",

                "author_id":
                    author_id
            }), 400

        authors.append(author)


    book = Book(
        title=payload["title"],
        isbn=payload["isbn"],
        price_vnd=
            payload["price_vnd"],
        stock=
            payload.get(
                "stock",
                0
            ),
        category=category,
        authors=authors
    )


    db.session.add(book)
    db.session.commit()


    response = jsonify(
        book.to_dict()
    )

    response.status_code = 201

    response.headers[
        "Location"
    ] = (
        f"/api/v1/books/{book.id}"
    )

    return response


# ============================================================
# PATCH
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


    payload = (
        request.get_json(
            silent=True
        )
        or {}
    )


    if "title" in payload:

        title = str(
            payload["title"]
        ).strip()

        if not title:

            return jsonify({
                "error":
                    "title_empty"
            }), 400

        book.title = title


    if "price_vnd" in payload:

        price = payload[
            "price_vnd"
        ]

        if (
            not isinstance(
                price,
                int
            )
            or price < 0
        ):

            return jsonify({
                "error":
                    "invalid_price"
            }), 400

        book.price_vnd = price


    if "stock" in payload:

        stock = payload["stock"]

        if (
            not isinstance(
                stock,
                int
            )
            or stock < 0
        ):

            return jsonify({
                "error":
                    "invalid_stock"
            }), 400

        book.stock = stock


    if "category_id" in payload:

        category = db.session.get(
            Category,
            payload[
                "category_id"
            ]
        )

        if category is None:

            return jsonify({
                "error":
                    "category_not_found"
            }), 400

        book.category = category


    if "author_ids" in payload:

        authors = []

        for author_id in payload[
            "author_ids"
        ]:

            author = db.session.get(
                Author,
                author_id
            )

            if author is None:

                return jsonify({
                    "error":
                        "author_not_found",
                    "author_id":
                        author_id
                }), 400

            authors.append(
                author
            )

        book.authors = authors


    db.session.commit()

    return jsonify(
        book.to_dict()
    ), 200


# ============================================================
# DELETE
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