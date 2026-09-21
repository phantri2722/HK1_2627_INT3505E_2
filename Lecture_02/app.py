from flask import Flask, jsonify, request, make_response

app = Flask(__name__)

BOOKS = [
    {"id": 1, "title": "Clean Code", "author": "Robert Martin"},
    {"id": 2, "title": "Clean Architecture", "author": "Robert Martin"},
    {"id": 3, "title": "Fluent Python", "author": "Luciano Ramalho"},
    {"id": 4, "title": "Effective Python", "author": "Brett Slatkin"},
    {"id": 5, "title": "Python Crash Course", "author": "Eric Matthes"},
    {"id": 6, "title": "Designing Data-Intensive Applications", "author": "Martin Kleppmann"},
]

# pagination parameters
DEFAULT_SIZE = 20
MAX_SIZE = 100

# List + Filter + Pagination + Links
@app.route('/books', methods=['GET'])
def list_books():
    try:
        page = int(request.args.get('page', 1))
        size = int(request.args.get('size', DEFAULT_SIZE))
    except ValueError:
        return jsonify(error="Page and size must be integers"), 400

    page = max(page, 1)
    size = max(min(size, MAX_SIZE), 1)

    fit = BOOKS

    a = request.args.get("author")
    if a:
        fit = [b for b in fit if b["author"].lower() == a.lower()]

    q = (request.args.get("q") or "").lower()
    if q:
        fit = [b for b in fit if q in b["title"].lower()]

    # pagination
    total = len(fit)
    start = (page - 1) * size
    end = start + size

    items = fit[start:end]
    last = (total + size - 1) // size

    #HATEOAS links
    def u(p):
        return f"/books?page={p}&size={size}"

    links = {
        "self": {"href": u(page)},
        "first": {"href": u(1)},
        "last": {"href": u(last)},
    }

    if page > 1:
        links["prev"] = {"href": u(page - 1)}
    if end < total:
        links["next"] = {"href": u(page + 1)}

    body = {
        "data": items,
        "pagination": {
            "page": page,
            "size": size,
            "total": total,
        },
        "_links": links
    }

    resp = make_response(jsonify(body), 200)
    resp.headers["Cache-Control"] = "public, max-age=30"

    return resp