from marshmallow import fields, validate
from marshmallow_enum import EnumField
from schemas import ma


class TransactionAPISchema(ma.Schema):
    sender           = fields.String()
    receiver         = fields.String()
    amount           = fields.String()



class AddNodeAPISchema(ma.Schema):
    nodes           = fields.List(fields.Integer(),missing=[],many=True)