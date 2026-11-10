from flask import Flask
from flask_smorest import Api

from extensions import db
from models.orders import Order, OrderItem
from models.products import Product
from routes.products import products_bp
from routes.orders import orders_bp


def create_app():
    app = Flask(__name__)

    app.config.update(
        SQLALCHEMY_DATABASE_URI="sqlite:///products.db",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,

        API_TITLE="Product and Order API",
        API_VERSION="1.0.0",
        OPENAPI_VERSION="3.0.3",

        OPENAPI_URL_PREFIX="/",
        OPENAPI_JSON_PATH="openapi.json",
        OPENAPI_SWAGGER_UI_PATH="/docs",
        OPENAPI_SWAGGER_UI_URL=(
            "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
        ),
    )

    db.init_app(app)

    api = Api(app)
    api.register_blueprint(products_bp)
    api.register_blueprint(orders_bp)

    with app.app_context():
        db.create_all()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)