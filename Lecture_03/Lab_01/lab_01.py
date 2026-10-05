from flask import Flask, jsonify, request, make_response

app = Flask(__name__)

POSTS = []
next_id = 1


@app.get("/api/v1/posts")
def list_posts():
    return jsonify({
        "data": POSTS,
        "total": len(POSTS)
    }), 200


@app.post("/api/v1/posts")
def create_post():
    global next_id

    if not request.is_json:
        return jsonify({
            "error": "Content-Type must be application/json"
        }), 415

    body = request.get_json(silent=True) or {}

    title = (body.get("title") or "").strip()
    content = (body.get("content") or "").strip()
    author_id = body.get("author_id")

    if not title or not content or author_id is None:
        return jsonify({
            "error": "title, content and author_id are required"
        }), 422

    post = {
        "id": next_id,
        "author_id": author_id,
        "title": title,
        "content": content,
        "tags": []
    }

    POSTS.append(post)
    next_id += 1

    response = make_response(jsonify(post), 201)

    response.headers["Location"] = (
        f"/api/v1/posts/{post['id']}"
    )

    return response


if __name__ == "__main__":
    app.run(debug=True)