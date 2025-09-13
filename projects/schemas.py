from flask_marshmallow import Schema
from marshmallow.fields import String, Integer, DateTime, Nested


class ProjectSchema(Schema):
    id = Integer(dump_only=True)
    name = String(required=True)
    description = String()
    status = String(dump_only=True)
    created_at = DateTime(dump_only=True)
    updated_at = DateTime(dump_only=True)
    creator_id = Integer(dump_only=True)

    creator = Nested(
        "users.schemas.UserSchema",
        only=("id", "username", "email"),
        dump_only=True,
    )
    members = Nested(
        "users.schemas.UserSchema",
        many=True,
        only=("id", "username", "email"),
        dump_only=True,
    )
