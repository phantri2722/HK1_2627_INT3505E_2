from flask import Flask

from models import (
    db,
    Category,
    Author,
    User
)

from routes.books import books_bp


def create_app():

    app = Flask(__name__)


    # ========================================================
    # Database configuration
    # ========================================================

    app.config[
        "SQLALCHEMY_DATABASE_URI"
    ] = "sqlite:///bookstore.db"

    app.config[
        "SQLALCHEMY_TRACK_MODIFICATIONS"
    ] = False


    db.init_app(app)


    # ========================================================
    # Register routes
    # ========================================================

    app.register_blueprint(
        books_bp
    )


    # ========================================================
    # Initialize database
    # ========================================================

    with app.app_context():

        db.create_all()

        seed_database()


    return app


# ============================================================
# Add some sample data
# ============================================================

def seed_database():

    if Category.query.count() == 0:

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


    if Author.query.count() == 0:

        author1 = Author(
            name="Robert C. Martin",
            bio="Software engineer and author."
        )

        author2 = Author(
            name="Martin Kleppmann",
            bio="Researcher and author."
        )

        db.session.add_all([
            author1,
            author2
        ])


    if User.query.count() == 0:

        user = User(
            email="student@example.com",
            display_name="Student"
        )

        db.session.add(user)


    db.session.commit()


# ============================================================
# Run
# ============================================================

if __name__ == "__main__":

    app = create_app()

    app.run(
        debug=True
    )