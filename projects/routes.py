from flask import Blueprint, jsonify


projects = Blueprint("projects", __name__)


@projects.route("/projects")
def get_projects():
  """Get all projects"""
  projects_list = [
    {"id": 1, "name": "Building project management tool", "status": "In Progress"},
    {"id": 2, "name": "Deploy to server", "status": "In Progress"},
  ]
  return jsonify(projects_list)
