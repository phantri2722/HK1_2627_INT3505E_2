from flask import Flask, jsonify, request
from uuid import uuid4
app = Flask(__name__)
BOOKS = {
    1: {"id": 1, "title": "Book 1"},
    2: {"id": 2, "title": "Book 2"},
    3: {"id": 3, "title": "Book 3"},
    4: {"id": 4, "title": "Book 4"},
    5: {"id": 5, "title": "Book 5"},
    6: {"id": 6, "title": "Book 5"},
    7: {"id": 7, "title": "Book 5"},
    8: {"id": 8, "title": "Book 5"},
    9: {"id": 9, "title": "Book 5"},
    10: {"id": 10, "title": "Book 5"},
}

def find_by_id(book_id):
    for book in BOOKS.values():
        if book["id"] == int(book_id):
            return book
    return None

@app.route("/books/<book_id>", methods=["GET"])
def get_book(book_id):
    book = find_by_id(book_id)
    if book is None:
        return jsonify({"Error": "not found"}), 404
    return jsonify(book), 200


@app.route("/items/<int:item_id>")
def get_item(item_id):# int sẵn
    return jsonify({"id": item_id}), 200

@app.route("/books", methods=["GET"])
def list_books():
    limit = int(request.args.get("limit", 20))
    q = request.args.get("q", "").strip().lower()
    if limit < 1:
            return jsonify({"Error": "limit must be greater than 0"}), 400

    items = [b for b in BOOKS.values() if q in str(b["title"]).lower()]
    if items is None or len(items) == 0:
        return jsonify({"Error": "not found"}), 404
    
    return jsonify(items[:limit]), 200