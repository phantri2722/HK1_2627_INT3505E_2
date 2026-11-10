from marshmallow import Schema, fields, validate


class OrderItemIn(Schema):
    product_id = fields.Int(
        required=True,
        validate=validate.Range(min=1)
    )

    qty = fields.Int(
        required=True,
        validate=validate.Range(min=1)
    )


class OrderIn(Schema):
    customer_name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100)
    )

    items = fields.List(
        fields.Nested(OrderItemIn),
        required=True,
        validate=validate.Length(min=1)
    )


class ProductBrief(Schema):
    id = fields.Int()
    sku = fields.Str()
    name = fields.Str()


class OrderItemOut(Schema):
    id = fields.Int()
    product_id = fields.Int()
    qty = fields.Int()
    unit_price_cents = fields.Int()
    line_total_cents = fields.Int()
    product = fields.Nested(ProductBrief)


class OrderOut(Schema):
    id = fields.Int()
    customer_name = fields.Str()
    status = fields.Str()
    total_cents = fields.Int()
    items = fields.Nested(OrderItemOut, many=True)