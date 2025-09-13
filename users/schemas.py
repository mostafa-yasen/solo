from flask_marshmallow import Schema
from marshmallow.fields import Integer, String, Email, Nested


class UserSchema(Schema):
    id = Integer(dump_only=True)
    username = String(required=True)
    email = Email(required=True)
    password = String(load_only=True, required=True)

    projects = Nested("ProjectSchema", many=True, dump_only=True)


class UserLoginSchema(Schema):
    username = String(required=True)
    password = String(required=True)


class UserLoginOutputSchema(Schema):
    access_token = String(dump_only=True)
