from flask import Flask, jsonify, request
app = Flask(__name__)
_next = 2
BOOKS = [{"id": 1, "title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "year": 1925}]

def find(bid):
    return next((b for b in BOOKS if b["id"] == bid), None)

# LIST — GET /books
@app.route("/books", methods=["GET"])
def list_books():
    bid = request.args.get("id")
    if bid is not None:
        try:
            bid = int(bid)
        except (TypeError, ValueError):
            return {"error":"id must be an integer"}, 400
        book = find(bid)
        if not book:
            return {"error":"not found"}, 404
        return jsonify(book), 200

    sort_by = request.args.get("sort")
    if sort_by is not None:
        if sort_by not in ("id", "title", "author", 'year'):
            return {"error":"invalid field"}, 400
        BOOKS.sort(key=lambda b: b[sort_by])
        return jsonify(BOOKS), 200

    n = int(request.args.get("limit", 100))
    BOOKS.sort(key=lambda b: b["id"])
    return jsonify(BOOKS[:n]), 200

# DETAIL — GET /books/<int:id>
@app.route("/books/<int:bid>", methods=["GET"])
def get_book(bid):
    book = find(bid)
    if not book: return {"error":"not found"}, 404
    return jsonify(book), 200

# CREATE — POST /books
@app.route("/books", methods=["POST"])
def create_book():
    global _next
    body = request.get_json(silent=True) or {}
    t, a, y = body.get("title"), body.get("author"), body.get("year")
    if not t or not a:
        return {"error":"need title+author"}, 400

    if isinstance(y, str):
        try:
            y = int(y)
        except ValueError:
            return {"error":"year must be an integer"}, 400

    if y is not None and (y < 1900):
        return {"error":"year must be larger or equal to 1900"}, 400
    
    book = {"id":_next, "title":t, "author":a, "year":y}
    _next += 1; BOOKS.append(book)
    return jsonify(book), 201, {"Location":f"/books/{book['id']}"}

# UPDATE — PUT, DELETE — DELETE 
@app.route("/books/<int:bid>", methods=["PUT", "DELETE"])
def modify_book(bid):
    book = find(bid)
    if not book:
        return {"error":"not found"}, 404
    if request.method == "PUT":
        book.update(request.get_json(silent=True) or {})
        return jsonify(book), 200
    BOOKS.remove(book)
    return "", 204