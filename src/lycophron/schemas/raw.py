from marshmallow import fields, Schema

class Raw(Schema):
    blob = fields.Dict(keys=fields.String())