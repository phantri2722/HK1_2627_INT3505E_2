from flask_smorest import Blueprint, abort
from sqlalchemy import func, update
from sqlalchemy.exc import IntegrityError

from extensions import db
from models import Product
from schemas import (
    ProductIn,
    ProductOut,
    ProductPatch,
    ReserveIn,
    PaginationQuery,
    ProductPage,
)


products_bp = Blueprint(
    "Products",
    __name__,
    url_prefix="/api/v1/products",
    description="Product management operations",
)


@products_bp.route("", methods=["GET"])
@products_bp.arguments(PaginationQuery, location="query")
@products_bp.response(200, ProductPage)
def list_products(pagination):
    """List products with pagination."""

    page = pagination["page"]
    size = pagination["size"]

    total = db.session.scalar(
        db.select(func.count(Product.id)).where(
            Product.archived.is_(False)
        )
    )

    statement = (
        db.select(Product)
        .where(Product.archived.is_(False))
        .order_by(Product.id)
        .offset((page - 1) * size)
        .limit(size)
    )

    products = db.session.execute(
        statement
    ).scalars().all()

    return {
        "items": products,
        "page": page,
        "size": size,
        "total": total,
    }

@products_bp.route("/<int:id>", methods=["GET"])
@products_bp.response(200, ProductOut)
def get_product(id):
    """Retrieve a product by ID."""

    product = db.session.get(Product, id)

    if product is None or product.archived:
        abort(404, message="Product not found")

    return product

@products_bp.route("", methods=["POST"])
@products_bp.arguments(ProductIn)
@products_bp.response(201, ProductOut)
def create_product(data):
    """Create a new product."""

    product = Product(**data)

    try:
        db.session.add(product)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        abort(409, message="Product conflicts with database constraints")

    return product

@products_bp.route("/<int:id>", methods=["PATCH"])
@products_bp.arguments(ProductPatch)
@products_bp.response(200, ProductOut)
def update_product(data, id):
    """Partially update a product."""

    product = db.session.get(Product, id)

    if product is None or product.archived:
        abort(404, message="Product not found")

    for field, value in data.items():
        setattr(product, field, value)

    db.session.commit()

    return product

@products_bp.route("/<int:id>", methods=["DELETE"])
@products_bp.response(204)
def delete_product(id):
    """Soft-delete a product."""

    product = db.session.get(Product, id)

    if product is None or product.archived:
        abort(404, message="Product not found")

    product.archived = True
    db.session.commit()

    return None

@products_bp.route("/<int:id>/reserve", methods=["POST"])
@products_bp.arguments(ReserveIn)
@products_bp.response(200, ProductOut)
def reserve_product(data, id):
    """Reserve product stock."""

    qty = data["qty"]

    statement = (
        update(Product)
        .where(
            Product.id == id,
            Product.archived.is_(False),
            Product.qty_in_stock >= qty,
        )
        .values(
            qty_in_stock=Product.qty_in_stock - qty
        )
    )

    result = db.session.execute(statement)

    if result.rowcount == 0:
        db.session.rollback()

        product = db.session.get(Product, id)

        if product is None or product.archived:
            abort(404, message="Product not found")

        abort(409, message="Insufficient stock")

    db.session.commit()

    return db.session.get(Product, id)