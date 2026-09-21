import sqlite3
from flask import Flask, jsonify, request, make_response
import hashlib

app = Flask(__name__)

DATABASE = "books.db"

# pagination parameters
DEFAULT_SIZE = 20
MAX_SIZE = 100

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()

    conn.execute("""
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        price FLOAT NOT NULL)
    """)
    conn.commit()
    conn.close()

def generate_etag(title, author, price):
    etag_string = f"{title}:{author}:{price}"
    return hashlib.md5(etag_string.encode()).hexdigest()

# List + Filter + Pagination + Links
@app.route("/books", methods=["GET"])
def list_books():
    try:
        page = int(request.args.get("page", 1))
        size = int(request.args.get("size", DEFAULT_SIZE))
    except ValueError:
        return jsonify(error="Page and size must be integers"), 400

    page = max(page, 1)
    size = max(min(size, MAX_SIZE), 1)

    a = request.args.get("author")
    q = request.args.get("title", "")

    conn = get_db()

    conditions = []
    params = []

    if a:
        conditions.append("LOWER(author) = LOWER(?)")
        params.append(a)

    if q:
        conditions.append("LOWER(title) LIKE LOWER(?)")
        params.append(f"%{q}%")

    where_clause = ""

    if conditions:
        where_clause = " WHERE " + " AND ".join(conditions)

    count_query = f"""
        SELECT COUNT(*)
        FROM books
        {where_clause}
    """

    total = conn.execute(
        count_query,
        params
    ).fetchone()[0]

    offset = (page - 1) * size

    data_query = f"""
        SELECT id, title, author, price
        FROM books
        {where_clause}
        ORDER BY id
        LIMIT ? OFFSET ?
    """

    rows = conn.execute(
        data_query,
        params + [size, offset]
    ).fetchall()

    items = [dict(row) for row in rows]

    last = max((total + size - 1) // size, 1)

    def u(p):
        return f"/books?page={p}&size={size}"

    links = {
        "self": {"href": u(page)},
        "first": {"href": u(1)},
        "last": {"href": u(last)},
    }

    if page > 1:
        links["prev"] = {"href": u(page - 1)}

    if offset + size < total:
        links["next"] = {"href": u(page + 1)}

    body = {
        "data": items,
        "pagination": {
            "page": page,
            "size": size,
            "total": total,
        },
        "_links": links,
    }

    conn.close()

    resp = make_response(jsonify(body), 200)
    resp.headers["Cache-Control"] = "public, max-age=30"

    return resp

@app.route("/books", methods=["POST"])
def create_book():
    data = request.get_json()

    title = data.get("title")
    author = data.get("author")
    price = data.get("price")

    if not title or not author or price is None:
        return jsonify(error="Title, author, and price are required"), 400

    if price < 0:
        return jsonify(error="Price must be non-negative"), 400

    etag = generate_etag(title, author, price)
    
    conn = get_db()

    cursor = conn.execute(
        "INSERT INTO books (title, author, price, etag) VALUES (?, ?, ?)",
        (title, author, price, etag)
    )

    conn.commit()

    book_id = cursor.lastrowid

    conn.close()

    return jsonify({
        "id": book_id,
        "title": title,
        "author": author,
        "price": price
    }), 201

@app.route("/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    conn = get_db()

    book = conn.execute(
        """
        SELECT id, title, author, price, etag
        FROM books
        WHERE id = ?
        """,
        (book_id,)
    ).fetchone()

    conn.close()

    if book is None:
        return jsonify(error="Book not found"), 404

    etag = book["etag"]

    client_etag = request.headers.get("If-None-Match")

    if client_etag == f'"{etag}"':
        return "", 304

    body = {
        "id": book["id"],
        "title": book["title"],
        "author": book["author"],
        "price": book["price"]
    }

    response = make_response(jsonify(body), 200)

    response.headers["ETag"] = f'"{etag}"'

    return response

if __name__ == "__main__":
    init_db()
    app.run(debug=True)