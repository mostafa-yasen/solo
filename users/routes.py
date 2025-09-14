from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from users.models import User
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from users.schemas import UserSchema, UserLoginSchema, UserLoginOutputSchema


users = Blueprint("users", __name__)


@users.route("/register", methods=["POST"])
def register_user():
    try:
        validated_data = UserSchema().load(request.json)
    except ValidationError as err:
        return (
            jsonify(
                {
                    "message": "Missing required fields",
                    "error": err.messages,
                }
            ),
            400,
        )

    username = validated_data.get("username")
    email = validated_data.get("email")
    password = validated_data.get("password")

    hashed_password = generate_password_hash(password)
    new_user = User(
        username=username,
        email=email,
        password_hash=hashed_password,
    )

    try:
        db.session.add(new_user)
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"message": "User already exists", "error": str(e)}), 409

    return (
        jsonify({"message": "User registered successfully", "data": validated_data}),
        201,
    )


@users.route("/register", methods=["GET"])
def registration_page():
    return "User registration page"


@users.route("/login", methods=["POST"])
def login():
    try:
        validated_data = UserLoginSchema().load(request.json)
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400

    username = validated_data.get("username")
    password = validated_data.get("password")

    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password_hash, password):
        access_token = create_access_token(identity=str(user.id))
        user_login_output = UserLoginOutputSchema().dump({"access_token": access_token})
        return (
            jsonify({"message": "Login successful", "data": user_login_output}),
            200,
        )

    return (
        jsonify(
            {
                "message": "Invalid credentials",
                "error": "Invalid credentials",
            }
        ),
        401,
    )


@users.route("/login", methods=["GET"])
def login_page():
    return "User login page"


@users.route("/me", methods=["GET"])
@jwt_required()
def me():
    current_user_id = get_jwt_identity()
    user = db.session.get(User, current_user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    user_schema = UserSchema().dump(user)

    return (
        jsonify(
            {
                "message": "User information",
                "user": user_schema,
            }
        ),
        200,
    )
