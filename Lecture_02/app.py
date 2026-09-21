# app.py — bài 1: GET /books, POST /books
from flask import Flask, jsonify, make_response, request
app = Flask(__name__)
BOOKS = []
_next_id = 1

# ─── GET /books —— trả danh sách
@app.route("/books", methods=["GET"])
def list_books():
    return jsonify({
            "data": BOOKS,
            "total": len(BOOKS)
            }), 200

# ─── POST /books —— tạo mới
@app.route("/books", methods=["POST"])
def create_book():
    global _next_id
    if not request.is_json:
        return jsonify(error="expected JSON"), 415
    p = request.get_json(silent=True) or {}
    if not p:
        return jsonify(error="invalid JSON"), 400

    t = (p.get("title") or"").strip()
    a = (p.get("author") or"").strip()
    price = p.get("price")
    if not t or not a:
        return jsonify(error="title and author required"), 422
    if price is not None and price < 0:
        return jsonify(error="price must be positive"), 422
    book = {"id": _next_id, "title": t, "author": a, "price": price}
    BOOKS.append(book); _next_id += 1
    resp = make_response(jsonify(book), 201)
    resp.headers["Location"] = f"/books/{book['id']}"
    return resp

@app.route("/books/<int:bid>", methods=["GET"])
def fetch(bid):
    i = next((k for k,b in enumerate(BOOKS) if b["id"]==bid), None)
    if i is None: 
        return jsonify(error="not found"), 404
    resp = make_response(jsonify(BOOKS[i]), 200)
    resp.headers["Cache-Control"]="max-age=60"; 
    return resp

# ─── PUT ─── thay toàn bộ, title+author bắt buộc
@app.route("/books/<int:bid>", methods=["PUT"])
def put(bid):
    i = next((k for k,b in enumerate(BOOKS) if b["id"]==bid), None)
    if i is None:
        return jsonify(error="not found"), 404
    p = request.get_json(silent=True) or {}
    t,a = p.get("title"), p.get("author")
    if not t or not a: 
        return jsonify(error="need title+author"), 422
    BOOKS[i]={"id":bid,
              "title":t.strip(),
              "author":a.strip(),
              "price":p.get("price")}
    return jsonify(BOOKS[i]), 200

# ─── PATCH ─── chỉ cập nhật field có trong body
@app.route("/books/<int:bid>", methods=["PATCH"])
def patch(bid):
    i = next((k for k,b in enumerate(BOOKS) if b["id"]==bid), None)
    if i is None:
        return jsonify(error="not found"), 404
    p = request.get_json(silent=True) or {}
    if p.get("price", 0) < 0:
        return jsonify(error="price must be positive"), 422
    for k in"title author price".split():
        if k in p:
            BOOKS[i][k] = p[k]
            return jsonify(BOOKS[i]), 200

# ─── DELETE ─── idempotent, trả 204
@app.route("/books/<int:bid>", methods=["DELETE"])
def delete(bid):
    i = next((k for k,b in enumerate(BOOKS)
    if b["id"]==bid), None)
    if i is None: 
        return jsonify(error="not found"), 404
    BOOKS.pop(i);
    _next_id -= 1
    return "", 204
