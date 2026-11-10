from sqlalchemy import event

from extensions import db


PRODUCT_URL = "/api/v1/products"
ORDER_URL = "/api/v1/orders"


# --------------------------------------------------
# Test helpers
# --------------------------------------------------

def create_product(client, sku, name, price):
    """Create a product and return its ID."""

    response = client.post(
        PRODUCT_URL,
        json={
            "sku": sku,
            "name": name,
            "price_cents": price,
            "qty_in_stock": 100,
        },
    )

    assert response.status_code == 201

    return response.get_json()["id"]


def create_order(client, product_ids):
    """Create an order containing two units of each product."""

    response = client.post(
        ORDER_URL,
        json={
            "customer_name": "Alice",
            "items": [
                {
                    "product_id": product_id,
                    "qty": 2,
                }
                for product_id in product_ids
            ],
        },
    )

    assert response.status_code == 201

    return response.get_json()


def count_select_queries(client, engine):
    """
    Execute GET /orders and count SQL SELECT statements.

    Only SQL executed during the GET request is counted.
    """

    queries = []

    def capture_query(
        conn,
        cursor,
        statement,
        parameters,
        context,
        executemany,
    ):
        if statement.lstrip().upper().startswith("SELECT"):
            queries.append(statement)

    event.listen(
        engine,
        "before_cursor_execute",
        capture_query,
    )

    try:
        response = client.get(ORDER_URL)
    finally:
        event.remove(
            engine,
            "before_cursor_execute",
            capture_query,
        )

    assert response.status_code == 200

    return len(queries), response.get_json()


# --------------------------------------------------
# POST /api/v1/orders
# --------------------------------------------------

def test_create_order_with_multiple_items(client):
    keyboard_id = create_product(
        client,
        "KEYBOARD-001",
        "Mechanical Keyboard",
        4500,
    )

    mouse_id = create_product(
        client,
        "MOUSE-001",
        "Wireless Mouse",
        2500,
    )

    response = client.post(
        ORDER_URL,
        json={
            "customer_name": "Alice",
            "items": [
                {
                    "product_id": keyboard_id,
                    "qty": 2,
                },
                {
                    "product_id": mouse_id,
                    "qty": 1,
                },
            ],
        },
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["id"] > 0
    assert data["customer_name"] == "Alice"
    assert data["status"] == "created"
    assert data["total_cents"] == 11500

    assert len(data["items"]) == 2

    # Check OrderItem → Product relationships.
    product_skus = {
        item["product"]["sku"]
        for item in data["items"]
    }

    assert product_skus == {
        "KEYBOARD-001",
        "MOUSE-001",
    }

    # Confirm the order is stored in the database.
    get_response = client.get(
        f"{ORDER_URL}/{data['id']}"
    )

    assert get_response.status_code == 200
    assert get_response.get_json()["total_cents"] == 11500


def test_create_order_with_invalid_product(client):
    response = client.post(
        ORDER_URL,
        json={
            "customer_name": "Alice",
            "items": [
                {
                    "product_id": 9999,
                    "qty": 1,
                },
            ],
        },
    )

    assert response.status_code == 404

    # No order should have been created.
    list_response = client.get(ORDER_URL)

    assert list_response.status_code == 200
    assert list_response.get_json() == []


def test_create_order_with_invalid_quantity(client):
    product_id = create_product(
        client,
        "KEYBOARD-001",
        "Mechanical Keyboard",
        4500,
    )

    response = client.post(
        ORDER_URL,
        json={
            "customer_name": "Alice",
            "items": [
                {
                    "product_id": product_id,
                    "qty": -5,
                },
            ],
        },
    )

    assert response.status_code == 422


def test_create_order_with_duplicate_products(client):
    product_id = create_product(
        client,
        "KEYBOARD-001",
        "Mechanical Keyboard",
        4500,
    )

    response = client.post(
        ORDER_URL,
        json={
            "customer_name": "Alice",
            "items": [
                {
                    "product_id": product_id,
                    "qty": 2,
                },
                {
                    "product_id": product_id,
                    "qty": 3,
                },
            ],
        },
    )

    assert response.status_code == 422


# --------------------------------------------------
# GET /api/v1/orders/<id>
# --------------------------------------------------

def test_get_order_with_related_products(client):
    keyboard_id = create_product(
        client,
        "KEYBOARD-001",
        "Mechanical Keyboard",
        4500,
    )

    mouse_id = create_product(
        client,
        "MOUSE-001",
        "Wireless Mouse",
        2500,
    )

    order = create_order(
        client,
        [keyboard_id, mouse_id],
    )

    response = client.get(
        f"{ORDER_URL}/{order['id']}"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["id"] == order["id"]
    assert data["customer_name"] == "Alice"
    assert len(data["items"]) == 2

    # Two keyboards + two mice.
    assert data["total_cents"] == 14000

    for item in data["items"]:
        assert item["qty"] == 2
        assert item["product"]["id"] == item["product_id"]
        assert item["product"]["sku"]


def test_get_nonexistent_order(client):
    response = client.get(
        f"{ORDER_URL}/9999"
    )

    assert response.status_code == 404


# --------------------------------------------------
# GET /api/v1/orders — Eager loading
# --------------------------------------------------

def test_list_orders_with_related_products(client):
    keyboard_id = create_product(
        client,
        "KEYBOARD-001",
        "Mechanical Keyboard",
        4500,
    )

    mouse_id = create_product(
        client,
        "MOUSE-001",
        "Wireless Mouse",
        2500,
    )

    create_order(client, [keyboard_id, mouse_id])
    create_order(client, [keyboard_id])

    response = client.get(ORDER_URL)

    assert response.status_code == 200

    data = response.get_json()

    assert len(data) == 2

    assert len(data[0]["items"]) == 2
    assert len(data[1]["items"]) == 1

    for order in data:
        for item in order["items"]:
            assert item["product"]["id"] == item["product_id"]


def test_list_orders_avoids_n_plus_one(client, app):
    """
    Verify that query count stays constant when
    the number of orders increases.

    Expected SQL SELECT queries:
      1. Load Orders
      2. Load OrderItems
      3. Load Products
    """

    keyboard_id = create_product(
        client,
        "KEYBOARD-001",
        "Mechanical Keyboard",
        4500,
    )

    mouse_id = create_product(
        client,
        "MOUSE-001",
        "Wireless Mouse",
        2500,
    )

    # Create one order.
    create_order(
        client,
        [keyboard_id, mouse_id],
    )

    with app.app_context():
        one_count, one_orders = count_select_queries(
            client,
            db.engine,
        )

    assert len(one_orders) == 1
    assert one_count == 3

    # Create five additional orders.
    for _ in range(5):
        create_order(
            client,
            [keyboard_id, mouse_id],
        )

    with app.app_context():
        many_count, many_orders = count_select_queries(
            client,
            db.engine,
        )

    assert len(many_orders) == 6

    # More orders should not produce more SELECT queries.
    assert many_count == 3
    assert many_count == one_count