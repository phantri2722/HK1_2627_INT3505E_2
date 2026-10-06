from flask import Flask, jsonify, request
import base64
import json

app = Flask(__name__)


ORDERS = [
    {"id": 1, "customer_id": 101, "status": "paid",    "total": 120.5},
    {"id": 2, "customer_id": 102, "status": "pending", "total": 75.0},
    {"id": 3, "customer_id": 101, "status": "paid",    "total": 220.0},
    {"id": 4, "customer_id": 103, "status": "shipped", "total": 99.9},
    {"id": 5, "customer_id": 104, "status": "paid",    "total": 300.0},
    {"id": 6, "customer_id": 102, "status": "pending", "total": 45.0},
    {"id": 7, "customer_id": 101, "status": "shipped", "total": 180.0},
    {"id": 8, "customer_id": 105, "status": "paid",    "total": 500.0},
]


def encode_cursor(position):
    raw = json.dumps({"pos": position}).encode()
    return base64.urlsafe_b64encode(raw).decode()


def decode_cursor(cursor):
    try:
        raw = base64.urlsafe_b64decode(cursor.encode()).decode()
        data = json.loads(raw)

        position = data["pos"]

        if not isinstance(position, int) or position < 0:
            raise ValueError()

        return position

    except Exception:
        raise ValueError("Invalid cursor")


@app.get("/orders")
def get_orders():

    # --------------------------------------------------
    # 1. FILTERING
    # --------------------------------------------------

    items = ORDERS.copy()

    status = request.args.get("status")

    if status:
        items = [
            order
            for order in items
            if order["status"] == status
        ]


    customer_id = request.args.get("customer_id")

    if customer_id:
        try:
            customer_id = int(customer_id)
        except ValueError:
            return jsonify({
                "error": "customer_id must be an integer"
            }), 400

        items = [
            order
            for order in items
            if order["customer_id"] == customer_id
        ]


    # --------------------------------------------------
    # 2. SORTING
    # --------------------------------------------------

    sort = request.args.get("sort", "id")

    allowed_sort_fields = {
        "id",
        "total",
        "customer_id",
        "status"
    }

    if sort not in allowed_sort_fields:
        return jsonify({
            "error": f"Invalid sort field: {sort}"
        }), 400

    # descending by default, following the convention
    # discussed in the slide
    items.sort(
        key=lambda order: order[sort],
        reverse=True
    )


    # --------------------------------------------------
    # 3. CURSOR
    # --------------------------------------------------

    cursor = request.args.get("cursor")

    start = 0

    if cursor:
        try:
            start = decode_cursor(cursor)
        except ValueError:
            return jsonify({
                "error": "Invalid cursor"
            }), 400


    # --------------------------------------------------
    # 4. LIMIT
    # --------------------------------------------------

    try:
        limit = int(request.args.get("limit", 5))
    except ValueError:
        return jsonify({
            "error": "limit must be an integer"
        }), 400

    if limit < 1 or limit > 100:
        return jsonify({
            "error": "limit must be between 1 and 100"
        }), 400


    end = start + limit
    page_items = items[start:end]


    # --------------------------------------------------
    # 5. SPARSE FIELDSETS
    # --------------------------------------------------

    fields = request.args.get("fields")

    if fields:

        requested_fields = fields.split(",")

        valid_fields = {
            "id",
            "customer_id",
            "status",
            "total"
        }

        for field in requested_fields:
            if field not in valid_fields:
                return jsonify({
                    "error": f"Unknown field: {field}"
                }), 400

        page_items = [
            {
                field: order[field]
                for field in requested_fields
            }
            for order in page_items
        ]


    # --------------------------------------------------
    # 6. NEXT CURSOR
    # --------------------------------------------------

    next_cursor = None

    if end < len(items):
        next_cursor = encode_cursor(end)


    return jsonify({
        "data": page_items,
        "next_cursor": next_cursor,
        "has_more": next_cursor is not None
    }), 200


if __name__ == "__main__":
    app.run(debug=True)