import sqlite3
import hashlib

conn = sqlite3.connect("books.db")
conn.row_factory = sqlite3.Row


def generate_etag(title, author, price):
    content = f"{title}|{author}|{price}"
    return hashlib.sha256(content.encode()).hexdigest()


# Add column
try:
    conn.execute("ALTER TABLE books ADD COLUMN etag TEXT")
except sqlite3.OperationalError:
    # Column probably already exists
    pass


# Generate ETag for existing books
books = conn.execute(
    "SELECT id, title, author, price FROM books"
).fetchall()

for book in books:
    etag = generate_etag(
        book["title"],
        book["author"],
        book["price"]
    )

    conn.execute(
        "UPDATE books SET etag = ? WHERE id = ?",
        (etag, book["id"])
    )

conn.commit()
conn.close()