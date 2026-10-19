import pytest

from app import create_app
from models import (
    db,
    Book,
    Category
)


@pytest.fixture()
def app():

    app = create_app(
        {
            "TESTING": True,

            "SQLALCHEMY_DATABASE_URI":
                "sqlite:///:memory:"
        },
        seed=False
    )


    with app.app_context():

        tech = Category(
            name="Technology",
            slug="tech"
        )

        fiction = Category(
            name="Fiction",
            slug="fiction"
        )

        db.session.add_all([
            tech,
            fiction
        ])

        db.session.flush()


        books = [

            Book(
                title="Alpha",
                isbn="9780000000001",
                price_vnd=500000,
                stock=10,
                category=tech
            ),

            Book(
                title="Beta",
                isbn="9780000000002",
                price_vnd=500000,
                stock=20,
                category=tech
            ),

            Book(
                title="Gamma",
                isbn="9780000000003",
                price_vnd=400000,
                stock=30,
                category=tech
            ),

            Book(
                title="Delta",
                isbn="9780000000004",
                price_vnd=300000,
                stock=40,
                category=tech
            ),

            Book(
                title="Novel A",
                isbn="9780000000005",
                price_vnd=200000,
                stock=50,
                category=fiction
            )
        ]

        db.session.add_all(books)
        db.session.commit()


    yield app


    with app.app_context():
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


# ============================================================
# Offset pagination
# ============================================================

def test_offset_pagination(client):

    response = client.get(
        "/api/v1/books"
        "?strategy=offset"
        "&offset=0"
        "&limit=2"
    )

    assert response.status_code == 200

    body = response.get_json()

    assert len(body["data"]) == 2

    assert (
        body["pagination"]["strategy"]
        == "offset"
    )

    assert (
        body["pagination"]["total"]
        == 5
    )

    assert (
        body["pagination"]["has_more"]
        is True
    )


# ============================================================
# Genre filtering
# ============================================================

def test_genre_filter(client):

    response = client.get(
        "/api/v1/books"
        "?strategy=offset"
        "&genre=tech"
        "&limit=100"
    )

    body = response.get_json()

    assert response.status_code == 200
    assert len(body["data"]) == 4

    for book in body["data"]:

        assert (
            book["category"]["slug"]
            == "tech"
        )


# ============================================================
# Multi-key sorting
# ============================================================

def test_multi_key_sort(client):

    response = client.get(
        "/api/v1/books"
        "?strategy=offset"
        "&genre=tech"
        "&sort=-price,title"
        "&limit=10"
    )

    assert response.status_code == 200

    books = response.get_json()[
        "data"
    ]


    # Alpha + Beta have same price,
    # so title ASC breaks the tie.
    assert books[0]["title"] == "Alpha"
    assert books[1]["title"] == "Beta"

    assert (
        books[0]["price"]["amount"]
        == 500000
    )

    assert (
        books[1]["price"]["amount"]
        == 500000
    )

    assert (
        books[2]["price"]["amount"]
        == 400000
    )


# ============================================================
# Cursor pagination
# ============================================================

def test_cursor_pagination(client):

    first_response = client.get(
        "/api/v1/books"
        "?strategy=cursor"
        "&genre=tech"
        "&sort=-price,title"
        "&limit=2"
    )

    assert (
        first_response.status_code
        == 200
    )

    first = (
        first_response.get_json()
    )

    assert len(first["data"]) == 2

    cursor = first[
        "pagination"
    ]["next_cursor"]

    assert cursor is not None


    first_ids = {
        book["id"]
        for book in first["data"]
    }


    second_response = client.get(
        "/api/v1/books"
        "?strategy=cursor"
        "&genre=tech"
        "&sort=-price,title"
        "&limit=2"
        f"&cursor={cursor}"
    )

    assert (
        second_response.status_code
        == 200
    )

    second = (
        second_response.get_json()
    )


    second_ids = {
        book["id"]
        for book in second["data"]
    }


    # No duplicate between pages
    assert first_ids.isdisjoint(
        second_ids
    )


# ============================================================
# Invalid cursor
# ============================================================

def test_invalid_cursor(client):

    response = client.get(
        "/api/v1/books"
        "?strategy=cursor"
        "&cursor=not-a-valid-cursor"
    )

    assert response.status_code == 400


# ============================================================
# Cursor must not be reused with different sort
# ============================================================

def test_cursor_sort_mismatch(client):

    first = client.get(
        "/api/v1/books"
        "?strategy=cursor"
        "&sort=-price"
        "&limit=2"
    ).get_json()


    cursor = first[
        "pagination"
    ]["next_cursor"]


    response = client.get(
        "/api/v1/books"
        "?strategy=cursor"
        "&sort=title"
        "&limit=2"
        f"&cursor={cursor}"
    )


    assert response.status_code == 400

    assert (
        response.get_json()["error"]
        == "cursor_sort_mismatch"
    )


# ============================================================
# Invalid sort field
# ============================================================

def test_invalid_sort(client):

    response = client.get(
        "/api/v1/books"
        "?sort=password"
    )

    assert response.status_code == 400

    assert (
        response.get_json()["error"]
        == "invalid_sort"
    )