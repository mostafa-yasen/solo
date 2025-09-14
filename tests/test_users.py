import pytest

from users.models import User


@pytest.fixture
def test_client(client, db_session):
    yield client
    db_session.rollback()


def test_register_user_success(test_client, db_session):
    """Test user registration success case"""
    data = {
        "username": "testuser",
        "password": "testpass",
        "email": "testuser@example.com",
    }
    response = test_client.post("/register", json=data)
    assert response.status_code == 201
    assert "User registered successfully" in response.get_json()["message"]

    user = User.query.filter_by(username="testuser").first()
    assert user is not None
    assert user.email == "testuser@example.com"


def test_register_user_missing_fields(test_client):
    """Test user registration with missing fields"""
    data = {"username": "testuser"}
    response = test_client.post("/register", json=data)
    assert response.status_code == 400
    assert "Missing required fields" in response.get_json()["message"]


def test_register_user_duplicate_username(test_client, db_session):
    """Test user registration with duplicate username"""
    answer = test_client.post(
        "/register",
        json={
            "username": "existinguser",
            "password": "testpassword",
            "email": "existinguser@example.com",
        },
    )
    assert answer.status_code == 201

    data = {
        "username": "anotheruser",
        "password": "anotherpassword",
        "email": "existinguser@example.com",
    }
    response = test_client.post("/register", json=data)
    assert response.status_code == 409
    assert "User already exists" in response.get_json()["message"]


def test_login_success(test_client, db_session):
    """Test user login success case"""
    register_response = test_client.post(
        "/register",
        json={
            "username": "testloginuser",
            "password": "testpass",
            "email": "testloginuser@example.com",
        },
    )
    assert register_response.status_code == 201

    login_response = test_client.post(
        "/login",
        json={
            "username": "testloginuser",
            "password": "testpass",
        },
    )
    assert login_response.status_code == 200
    assert "access_token" in login_response.get_json()["data"]
    assert login_response.get_json()["data"]["access_token"] is not None


def test_login_invalid_credentials(test_client):
    """Test user login with invalid credentials"""
    register_response = test_client.post(
        "/register",
        json={
            "username": "testinvaliduser",
            "password": "correctpass",
            "email": "testinvaliduser@example.com",
        },
    )
    assert register_response.status_code == 201

    login_response = test_client.post(
        "/login",
        json={
            "username": "testinvaliduser",
            "password": "wrongpass",
        },
    )
    assert login_response.status_code == 401
    assert "Invalid credentials" in login_response.get_json()["message"]


def test_login_with_non_existent_username(test_client):
    """Test user login with non-existent username"""
    login_response = test_client.post(
        "/login",
        json={
            "username": "nonexistentuser",
            "password": "somepass",
        },
    )
    assert login_response.status_code == 401
    assert "Invalid credentials" in login_response.get_json()["message"]


def test_get_current_user(logged_in_client):
    """Test retrieving current user info with valid token"""
    response = logged_in_client.get("/me")
    assert response.status_code == 200
    assert "user" in response.json
    assert "email" in response.json["user"]
    assert "username" in response.json["user"]
    assert "test_user" == response.json["user"]["username"]
    assert "test@example.com" == response.json["user"]["email"]


def test_get_current_user_unauthorized(test_client):
    """Test retrieving current user information without a token."""
    response = test_client.get("/me")

    assert response.status_code == 401
    assert "Missing Authorization Header" in response.json["msg"]
