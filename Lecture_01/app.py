from flask import Flask, jsonify

app = Flask(__name__)
ORDERS = {
    "1": {"id": "1", "status": "pending"},
    "2": {"id": "2", "status": "shipped"},
    "3": {"id": "3", "status": "delivered"},
    "4": {"id": "4", "status": "pending"},
    "5": {"id": "5", "status": "pending"},
    "6": {"id": "6", "status": "shipped"},
}

# DELETE /orders/<id>
@app.route("/orders/<id>", methods=["DELETE"])
def delete_order(id):
    order = ORDERS.get(id)
    # 404 — không tìm thấy
    if order is None:
        return {"error":"not found"}, 404
    # 409 — business rule
    if order["status"] in ("shipped","delivered"):
        return {"error":"cannot delete"}, 409
    ORDERS.pop(id, None)
    # 204 — success, no body
    return "", 204
