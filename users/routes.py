from flask import Blueprint

users = Blueprint("users", __name__)


@users.route("/register")
def registration():
    return "User registration page"


@users.route("/login")
def login():
    return "User login page"
