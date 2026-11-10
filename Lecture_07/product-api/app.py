from flask import Flask
from flask_smorest import Api

from extensions import db
from models.products import Product
from models.orders import Order, OrderItem

from routes.products import products_bp
from routes.orders import orders_bp


def create_app(test_config=None):
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

    if test_config is not None:
        app.config.update(test_config)

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