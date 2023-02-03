from marshmallow import Schema, fields


class APIResponse(Schema):
    __tablename__ = "api_response"
    response = fields.Dict(is_required=True)
