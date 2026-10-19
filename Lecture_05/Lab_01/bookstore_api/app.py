from flask import Flask

from models import (
    db,
    Category,
    Author,
    User,
    Book
)

from routes.books import (
    books_bp
)


def create_app(
    test_config=None,
    seed=True
):

    app = Flask(__name__)


    app.config.update({
        "SQLALCHEMY_DATABASE_URI":
            "sqlite:///bookstore.db",

        "SQLALCHEMY_TRACK_MODIFICATIONS":
            False
    })


    if test_config:
        app.config.update(
            test_config
        )


    db.init_app(app)

    app.register_blueprint(
        books_bp
    )


    with app.app_context():

        db.create_all()

        if seed:
            seed_database()


    return app


def seed_database():

    # --------------------------------------------------------
    # Categories
    # --------------------------------------------------------

    tech = Category.query.filter_by(
        slug="tech"
    ).first()

    if tech is None:

        tech = Category(
            name="Technology",
            slug="tech"
        )

        db.session.add(tech)


    fiction = Category.query.filter_by(
        slug="fiction"
    ).first()

    if fiction is None:

        fiction = Category(
            name="Fiction",
            slug="fiction"
        )

        db.session.add(fiction)


    db.session.flush()


    # --------------------------------------------------------
    # Authors
    # --------------------------------------------------------

    martin = Author.query.filter_by(
        name="Robert C. Martin"
    ).first()

    if martin is None:

        martin = Author(
            name="Robert C. Martin",
            bio="Software engineer and author."
        )

        db.session.add(martin)


    kleppmann = Author.query.filter_by(
        name="Martin Kleppmann"
    ).first()

    if kleppmann is None:

        kleppmann = Author(
            name="Martin Kleppmann",
            bio="Researcher and author."
        )

        db.session.add(kleppmann)


    ramalho = Author.query.filter_by(
        name="Luciano Ramalho"
    ).first()

    if ramalho is None:

        ramalho = Author(
            name="Luciano Ramalho"
        )

        db.session.add(ramalho)


    db.session.flush()


    # --------------------------------------------------------
    # User
    # --------------------------------------------------------

    if User.query.count() == 0:

        db.session.add(
            User(
                email=
                    "student@example.com",

                display_name=
                    "Student"
            )
        )


    # --------------------------------------------------------
    # Books
    # --------------------------------------------------------

    if Book.query.count() == 0:

        books = [

            Book(
                title="Clean Code",
                isbn="9780132350884",
                price_vnd=450000,
                stock=20,
                category=tech,
                authors=[martin]
            ),

            Book(
                title=
                    "Clean Architecture",
                isbn="9780134494166",
                price_vnd=450000,
                stock=12,
                category=tech,
                authors=[martin]
            ),

            Book(
                title=
                    "Designing Data-Intensive Applications",
                isbn="9781449373320",
                price_vnd=700000,
                stock=8,
                category=tech,
                authors=[kleppmann]
            ),

            Book(
                title="Fluent Python",
                isbn="9781492056355",
                price_vnd=500000,
                stock=15,
                category=tech,
                authors=[ramalho]
            ),

            Book(
                title="The Hobbit",
                isbn="9780547928227",
                price_vnd=250000,
                stock=25,
                category=fiction
            ),

            Book(
                title="Animal Farm",
                isbn="9780451526342",
                price_vnd=180000,
                stock=30,
                category=fiction
            )
        ]

        db.session.add_all(
            books
        )


    db.session.commit()


if __name__ == "__main__":

    app = create_app()

    app.run(debug=True)