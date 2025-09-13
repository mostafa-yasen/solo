from flask import Blueprint, jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from users.models import User
from sqlalchemy.exc import IntegrityError

users = Blueprint("users", __name__)


@users.route("/register", methods=["POST"])
def register_user():
    data = request.json
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not all([username, email, password]):
        return jsonify({"error": "Missing required fields"}), 400

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
        return jsonify({"error": str(e)}), 409

    return jsonify({"message": "User registered successfully", "data": data}), 201


@users.route("/register", methods=["GET"])
def registration_page():
    return "User registration page"


@users.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password_hash, password):
        return jsonify({"message": "Login successful"}), 200

    return jsonify({"error": "Invalid credentials"}), 401


@users.route("/login", methods=["GET"])
def login_page():
    return "User login page"
