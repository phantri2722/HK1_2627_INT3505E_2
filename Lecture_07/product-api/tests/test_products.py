PRODUCT_URL = "/api/v1/products"


def create_product(client, sku="KEYBOARD-001"):
    """Helper: create a product through the API."""

    response = client.post(
        PRODUCT_URL,
        json={
            "sku": sku,
            "name": "Mechanical Keyboard",
            "price_cents": 4500,
            "qty_in_stock": 10,
        },
    )

    assert response.status_code == 201
    return response.get_json()


def test_create_product(client):
    response = client.post(
        PRODUCT_URL,
        json={
            "sku": "MOUSE-001",
            "name": "Wireless Mouse",
            "price_cents": 2500,
            "qty_in_stock": 20,
        },
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["id"] > 0
    assert data["sku"] == "MOUSE-001"
    assert data["name"] == "Wireless Mouse"
    assert data["price_cents"] == 2500
    assert data["qty_in_stock"] == 20

    # Verify the product was saved in the database.
    get_response = client.get(
        f"{PRODUCT_URL}/{data['id']}"
    )

    assert get_response.status_code == 200
    assert get_response.get_json()["sku"] == "MOUSE-001"


def test_duplicate_sku(client):
    payload = {
        "sku": "MOUSE-001",
        "name": "Wireless Mouse",
        "price_cents": 2500,
    }

    first_response = client.post(
        PRODUCT_URL,
        json=payload,
    )

    assert first_response.status_code == 201

    second_response = client.post(
        PRODUCT_URL,
        json=payload,
    )

    assert second_response.status_code == 409

    # Only one product should exist.
    response = client.get(PRODUCT_URL)

    assert response.status_code == 200
    assert response.get_json()["total"] == 1


def test_invalid_product(client):
    response = client.post(
        PRODUCT_URL,
        json={
            "sku": "A",
            "name": "",
            "price_cents": -100,
        },
    )

    assert response.status_code == 422

    # Invalid data must not be inserted.
    get_response = client.get(PRODUCT_URL)

    assert get_response.status_code == 200
    assert get_response.get_json()["total"] == 0


def test_list_products_with_pagination(client):
    for i in range(5):
        create_product(
            client,
            sku=f"PRODUCT-{i:03d}",
        )

    response = client.get(
        f"{PRODUCT_URL}?page=2&size=2"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["page"] == 2
    assert data["size"] == 2
    assert data["total"] == 5
    assert len(data["items"]) == 2

    assert data["items"][0]["sku"] == "PRODUCT-002"
    assert data["items"][1]["sku"] == "PRODUCT-003"


def test_get_nonexistent_product(client):
    response = client.get(
        f"{PRODUCT_URL}/9999"
    )

    assert response.status_code == 404


def test_update_product(client):
    product = create_product(client)
    product_id = product["id"]

    response = client.patch(
        f"{PRODUCT_URL}/{product_id}",
        json={
            "name": "Updated Keyboard",
            "price_cents": 5000,
        },
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["name"] == "Updated Keyboard"
    assert data["price_cents"] == 5000

    # Fields not included in PATCH remain unchanged.
    assert data["sku"] == "KEYBOARD-001"
    assert data["qty_in_stock"] == 10


def test_reserve_product(client):
    product = create_product(client)
    product_id = product["id"]

    response = client.post(
        f"{PRODUCT_URL}/{product_id}/reserve",
        json={"qty": 3},
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["qty_in_stock"] == 7

    # Verify the updated stock was persisted.
    get_response = client.get(
        f"{PRODUCT_URL}/{product_id}"
    )

    assert get_response.get_json()["qty_in_stock"] == 7


def test_reserve_insufficient_stock(client):
    product = create_product(client)
    product_id = product["id"]

    response = client.post(
        f"{PRODUCT_URL}/{product_id}/reserve",
        json={"qty": 100},
    )

    assert response.status_code == 409

    # A failed reservation must not change stock.
    get_response = client.get(
        f"{PRODUCT_URL}/{product_id}"
    )

    assert get_response.status_code == 200
    assert get_response.get_json()["qty_in_stock"] == 10


def test_soft_delete_product(client):
    product = create_product(client)
    product_id = product["id"]

    response = client.delete(
        f"{PRODUCT_URL}/{product_id}"
    )

    assert response.status_code == 204

    # Archived product is not accessible by GET.
    get_response = client.get(
        f"{PRODUCT_URL}/{product_id}"
    )

    assert get_response.status_code == 404

    # Archived product is excluded from the list.
    list_response = client.get(PRODUCT_URL)

    assert list_response.status_code == 200
    assert list_response.get_json()["total"] == 0


def test_database_is_empty(client):
    """Verify that each test starts with a clean database."""

    response = client.get(PRODUCT_URL)

    assert response.status_code == 200

    data = response.get_json()

    assert data["items"] == []
    assert data["total"] == 0