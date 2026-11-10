from marshmallow import Schema, fields, validate


class ProductIn(Schema):
    sku = fields.Str(
        required=True,
        validate=validate.Length(min=3, max=32)
    )

    name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=255)
    )

    price_cents = fields.Int(
        required=True,
        validate=validate.Range(min=0)
    )

    qty_in_stock = fields.Int(
        load_default=0,
        validate=validate.Range(min=0)
    )


class ProductOut(Schema):
    id = fields.Int(dump_only=True)
    sku = fields.Str()
    name = fields.Str()
    price_cents = fields.Int()
    qty_in_stock = fields.Int()

class ProductPatch(Schema):
    name = fields.Str(
        validate=validate.Length(min=1, max=255)
    )

    price_cents = fields.Int(
        validate=validate.Range(min=0)
    )

    qty_in_stock = fields.Int(
        validate=validate.Range(min=0)
    )

class ReserveIn(Schema):
    qty = fields.Int(
        required=True,
        validate=validate.Range(min=1)
    )

class PaginationQuery(Schema):
    page = fields.Int(
        load_default=1,
        validate=validate.Range(min=1)
    )
    size = fields.Int(
        load_default=20,
        validate=validate.Range(min=1, max=100)
    )

class ProductPage(Schema):
    items = fields.Nested(ProductOut, many=True)
    page = fields.Int()
    size = fields.Int()
    total = fields.Int()

