from flask import Flask
from flask_smorest import Api

from extensions import db
from models import Product
from routes.products import products_bp


def create_app():
    app = Flask(__name__)

    app.config.update(
        # Database
        SQLALCHEMY_DATABASE_URI="sqlite:///products.db",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,

        # OpenAPI
        API_TITLE="Product API",
        API_VERSION="1.0.0",
        OPENAPI_VERSION="3.0.3",

        # Swagger UI
        OPENAPI_URL_PREFIX="/",
        OPENAPI_JSON_PATH="openapi.json",
        OPENAPI_SWAGGER_UI_PATH="/docs",
        OPENAPI_SWAGGER_UI_URL=(
            "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
        ),
    )

    db.init_app(app)

    # Register the Blueprint through flask-smorest
    api = Api(app)
    api.register_blueprint(products_bp)

    with app.app_context():
        db.create_all()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)