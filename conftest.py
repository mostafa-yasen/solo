import pytest
from app import app as flask_app, db
from werkzeug.security import generate_password_hash
from users.models import User


@pytest.fixture(scope="session")
def app():
    return flask_app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def db_session(app):
    with app.app_context():
        db.create_all()
        yield db.session
        db.drop_all()


@pytest.fixture
def logged_in_client(client, db_session):
    """Fixture that returns a test client with a valid access token."""
    # 1. Create and save a new user in the database
    hashed_password = generate_password_hash("password123")
    user = User(
        username="test_user",
        email="test@example.com",
        password_hash=hashed_password,
    )
    db_session.add(user)
    db_session.commit()

    login_data = {"username": "test_user", "password": "password123"}
    response = client.post("/login", json=login_data)
    assert "data" in response.json
    assert "access_token" in response.json["data"]
    access_token = response.json["data"]["access_token"]

    client.environ_base["HTTP_AUTHORIZATION"] = f"Bearer {access_token}"
    return client
