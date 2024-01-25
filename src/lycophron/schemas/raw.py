from marshmallow import Schema, fields


class Raw(Schema):
    blob = fields.Dict(keys=fields.String())
