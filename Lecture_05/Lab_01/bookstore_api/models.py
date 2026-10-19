from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import (
    Integer,
    String,
    Text,
    ForeignKey,
    Table,
    Column
)
from sqlalchemy.orm import mapped_column, relationship


db = SQLAlchemy()


# ============================================================
# Association table: Book <-> Author
# ============================================================

book_authors = Table(
    "book_authors",
    db.metadata,

    Column(
        "book_id",
        ForeignKey("book.id"),
        primary_key=True
    ),

    Column(
        "author_id",
        ForeignKey("author.id"),
        primary_key=True
    )
)


# ============================================================
# Category
# ============================================================

class Category(db.Model):

    id = mapped_column(
        Integer,
        primary_key=True
    )

    name = mapped_column(
        String(100),
        nullable=False
    )

    slug = mapped_column(
        String(100),
        unique=True,
        nullable=False
    )

    books = relationship(
        "Book",
        back_populates="category"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug
        }


# ============================================================
# Author
# ============================================================

class Author(db.Model):

    id = mapped_column(
        Integer,
        primary_key=True
    )

    name = mapped_column(
        String(100),
        nullable=False
    )

    bio = mapped_column(
        Text,
        nullable=True
    )

    books = relationship(
        "Book",
        secondary=book_authors,
        back_populates="authors"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "bio": self.bio
        }


# ============================================================
# Book
# ============================================================

class Book(db.Model):

    id = mapped_column(
        Integer,
        primary_key=True
    )

    title = mapped_column(
        String(200),
        nullable=False
    )

    isbn = mapped_column(
        String(13),
        unique=True,
        nullable=False
    )

    price_vnd = mapped_column(
        Integer,
        nullable=False
    )

    stock = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    category_id = mapped_column(
        ForeignKey("category.id"),
        nullable=False
    )

    category = relationship(
        "Category",
        back_populates="books"
    )

    authors = relationship(
        "Author",
        secondary=book_authors,
        back_populates="books"
    )

    reviews = relationship(
        "Review",
        back_populates="book",
        cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": f"book_{self.id}",
            "title": self.title,
            "isbn": self.isbn,
            "price": {
                "amount": self.price_vnd,
                "currency": "VND"
            },
            "stock": self.stock,

            "category": (
                self.category.to_dict()
                if self.category
                else None
            ),

            "authors": [
                author.to_dict()
                for author in self.authors
            ]
        }


# ============================================================
# User
# ============================================================

class User(db.Model):

    id = mapped_column(
        Integer,
        primary_key=True
    )

    email = mapped_column(
        String(255),
        unique=True,
        nullable=False
    )

    display_name = mapped_column(
        String(120),
        nullable=False
    )

    reviews = relationship(
        "Review",
        back_populates="user"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "display_name": self.display_name
        }


# ============================================================
# Review
# ============================================================

class Review(db.Model):

    id = mapped_column(
        Integer,
        primary_key=True
    )

    rating = mapped_column(
        Integer,
        nullable=False
    )

    comment = mapped_column(
        Text,
        nullable=True
    )

    book_id = mapped_column(
        ForeignKey("book.id"),
        nullable=False
    )

    user_id = mapped_column(
        ForeignKey("user.id"),
        nullable=False
    )

    book = relationship(
        "Book",
        back_populates="reviews"
    )

    user = relationship(
        "User",
        back_populates="reviews"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "rating": self.rating,
            "comment": self.comment,

            "user": (
                self.user.to_dict()
                if self.user
                else None
            )
        }