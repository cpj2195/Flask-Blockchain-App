from marshmallow import fields, validate
from marshmallow_enum import EnumField
from schemas import ma


class BlockchainSchema(ma.Schema):
    timestamp           = fields.String()
    proof               = fields.String()
    previous_hash       = fields.String()
    