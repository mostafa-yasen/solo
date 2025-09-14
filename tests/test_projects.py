from projects.models import Project
from users.models import User


def test_create_project_success(logged_in_client):
    """Test project creation success case"""
    project_data = {
        "name": "New Project",
        "description": "Project description",
    }
    response = logged_in_client.post(
        "/projects",
        json=project_data,
    )
    assert response.status_code == 201
    assert "id" in response.json
    assert "name" in response.json
    assert "description" in response.json
    assert response.json["name"] == project_data["name"]
    assert response.json["description"] == project_data["description"]


def test_create_project_missing_name(logged_in_client):
    """Test project creation with missing name"""
    project_data = {
        "description": "Project without a name",
    }
    response = logged_in_client.post(
        "/projects",
        json=project_data,
    )
    assert response.status_code == 400
    assert "name" in response.json
    assert "Missing data for required field." in response.json["name"]


def test_create_project_unauthorized(client):
    """Test project creation without authentication"""
    project_data = {
        "name": "Unauthorized Project",
        "description": "Should not be created",
    }
    response = client.post(
        "/projects",
        json=project_data,
    )
    assert response.status_code == 401
    assert "Missing Authorization Header" in response.json["msg"]


def test_get_projects_success(logged_in_client):
    """Test retrieving projects successfully"""
    project_data = {
        "name": "Project to Retrieve",
        "description": "This project will be retrieved",
    }
    create_response = logged_in_client.post(
        "/projects",
        json=project_data,
    )
    assert create_response.status_code == 201

    response = logged_in_client.get("/projects")
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert any(proj["name"] == project_data["name"] for proj in response.json)


def test_get_projects_filter_by_status(logged_in_client):
    """Test retrieving projects filtered by status"""
    active_project = {
        "name": "Active Project",
        "description": "This project is active",
    }
    completed_project = {
        "name": "Completed Project",
        "description": "This project is completed",
    }
    r = logged_in_client.post("/projects", json=active_project)
    assert r.status_code == 201, r.json

    r = logged_in_client.post("/projects", json=completed_project)
    assert r.status_code == 201, r.json
    completed_project_id = r.json["id"]

    r = logged_in_client.put(
        f"/projects/{completed_project_id}",
        json={"status": "Completed"},
    )
    assert r.status_code == 200, r.json

    response = logged_in_client.get("/projects?status=Active")
    assert response.status_code == 200, response.json
    assert isinstance(response.json, list), "Expected a list of projects"

    assert all(
        proj["status"] == "Active" for proj in response.json
    ), "Expected all projects to be Active"

    assert any(
        proj["name"] == active_project["name"] for proj in response.json
    ), "Expected active project to be in the list"
    assert all(
        proj["name"] != completed_project["name"] for proj in response.json
    ), "Expected completed project to not be in the list"


def test_update_project_forbidden(logged_in_client, db_session):
    """Test that user cannot update other user's project"""
    other_user = User(
        username="otheruser",
        email="otheruser@example.com",
        password_hash="hashedpassword",
    )
    db_session.add(other_user)
    db_session.commit()

    project = Project(
        name="Other user's project",
        description="Other user's project description",
        creator=other_user,
    )
    db_session.add(project)
    db_session.commit()

    data = {"name": "Attempted Update"}
    r = logged_in_client.put(f"/projects/{project.id}", json=data)

    assert r.status_code == 403, r.json
    assert "error" in r.json, r.json
    assert "You are not authorized to edit this project" in r.json["error"], r.json


def test_update_project_not_found(logged_in_client):
    """Tes update non-existing project"""
    data = {"name": "non-existing-project"}
    r = logged_in_client.put("/projects/999", json=data)

    assert r.status_code == 404, r.json


def test_delete_project_success(logged_in_client, db_session):
    """Test deleting project successfully"""
    user = db_session.get(User, 1)
    project = Project(name="To be deleted", creator=user)

    db_session.add(project)
    db_session.commit()

    r = logged_in_client.delete(f"/projects/{project.id}")
    assert r.status_code == 204, r.json

    project = db_session.get(Project, project.id)
    assert project is None, "Expected project to be deleted"


def test_delete_project_forbidden(logged_in_client, db_session):
    """Test that a user cannot delete another user's project."""
    other_user = User(
        username="otheruser",
        email="otheruser@example.com",
        password_hash="hashedpass",
    )
    db_session.add(other_user)
    db_session.commit()

    project = Project(
        name="Other user's project",
        description="Other user's project description",
        creator=other_user,
    )
    db_session.add(project)
    db_session.commit()

    r = logged_in_client.delete(f"/projects/{project.id}")
    assert r.status_code == 403, r.json
    assert "error" in r.json, r.json
    assert "You are not authorized to delete this project" in r.json["error"], r.json


def test_delete_project_not_found(logged_in_client):
    """Test deleting non-existing project"""
    r = logged_in_client.delete("/projects/999")
    assert r.status_code == 404, r.json
