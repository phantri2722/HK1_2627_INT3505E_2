from flask_smorest import Blueprint, abort
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from extensions import db
from models.orders import Order, OrderItem
from models.products import Product
from schemas.orders import OrderIn, OrderOut


orders_bp = Blueprint(
    "Orders",
    __name__,
    url_prefix="/api/v1/orders",
    description="Order management operations"
)


def order_query():
    """Load orders together with items and products."""
    return db.select(Order).options(
        selectinload(Order.items)
        .selectinload(OrderItem.product)
    )


# --------------------------------------------------
# POST /api/v1/orders
# --------------------------------------------------

@orders_bp.route("", methods=["POST"])
@orders_bp.arguments(OrderIn)
@orders_bp.response(201, OrderOut)
def create_order(data):
    """Create an order with one or more products."""

    customer_name = data["customer_name"]
    requested_items = data["items"]

    # Prevent the same product appearing twice.
    product_ids = [
        item["product_id"]
        for item in requested_items
    ]

    if len(product_ids) != len(set(product_ids)):
        abort(
            422,
            message="Duplicate product IDs are not allowed"
        )

    order = Order(
        customer_name=customer_name,
        status="created",
        total_cents=0
    )

    total = 0

    for item_data in requested_items:

        product_id = item_data["product_id"]
        qty = item_data["qty"]

        product = db.session.get(Product, product_id)

        if product is None or product.archived:
            abort(
                404,
                message=f"Product {product_id} not found"
            )

        # Price is taken from the database.
        unit_price = product.price_cents

        item = OrderItem(
            product=product,
            qty=qty,
            unit_price_cents=unit_price
        )

        order.items.append(item)

        total += qty * unit_price

    order.total_cents = total

    try:
        db.session.add(order)
        db.session.commit()

    except IntegrityError:
        db.session.rollback()
        abort(409, message="Order conflicts with database constraints")

    # Reload with relationships for response serialization.
    statement = order_query().where(Order.id == order.id)
    saved_order = db.session.scalar(statement)

    return saved_order


# --------------------------------------------------
# GET /api/v1/orders
# --------------------------------------------------

@orders_bp.route("", methods=["GET"])
@orders_bp.response(200, OrderOut(many=True))
def list_orders():
    """List orders and their items."""

    statement = order_query().order_by(Order.id)

    orders = db.session.execute(
        statement
    ).scalars().all()

    return orders


# --------------------------------------------------
# GET /api/v1/orders/<id>
# --------------------------------------------------

@orders_bp.route("/<int:id>", methods=["GET"])
@orders_bp.response(200, OrderOut)
def get_order(id):
    """Retrieve one order with its items."""

    statement = order_query().where(
        Order.id == id
    )

    order = db.session.scalar(statement)

    if order is None:
        abort(404, message="Order not found")

    return order