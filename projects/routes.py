import logging
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow.exceptions import ValidationError
from marshmallow import INCLUDE
from extensions import db
from projects.schemas import ProjectSchema
from projects.models import Project
from users.models import User

_logger = logging.getLogger(__name__)
projects = Blueprint("projects", __name__)
project_schema = ProjectSchema()
projects_schema = ProjectSchema(many=True)


@projects.route("/projects", methods=["POST"])
@jwt_required()
def create_project():
    """Create a new project"""
    try:
        data = project_schema.load(request.json)
    except ValidationError as err:
        msg = f"[API] [Create Project] Validation error during project creation: {err.messages}"
        _logger.error(msg)
        return jsonify(err.messages), 400

    current_user_id = get_jwt_identity()
    project = Project(
        name=data["name"],
        description=data["description"],
        creator_id=current_user_id,
    )
    db.session.add(project)
    db.session.commit()

    _logger.info(
        f"[API] [Create Project] New project created: {project.name} by user: {current_user_id}"
    )
    return project_schema.jsonify(project), 201


@projects.route("/projects", methods=["GET"])
@jwt_required()
def get_projects():
    """Get all projects for the current user"""
    current_user_id = get_jwt_identity()
    user = db.session.get(User, current_user_id)

    if not user:
        _logger.warning(f"[API] [Get Projects] User not found: {current_user_id}")
        return jsonify({"error": "User not found"}), 404

    status_filter = request.args.get("status")
    query = user.created_projects

    if status_filter:
        query = query.filter_by(status=status_filter)

    user_projects = query.all()
    _logger.info(
        f"[API] [Get Projects] Retrieved {len(user_projects)} projects for user: {current_user_id}"
    )
    return jsonify(projects_schema.dump(user_projects)), 200


@projects.route("/projects/<int:project_id>", methods=["GET"])
@jwt_required()
def get_project(project_id):
    """Get a specific project by ID"""
    current_user_id = get_jwt_identity()
    project = Project.query.filter(
        (Project.id == project_id) & (Project.creator_id == current_user_id)
    ).first()

    if not project:
        _logger.warning(
            f"[API] [Get Project] Project not found: {project_id} for user: {current_user_id}"
        )
        return jsonify({"msg": "Project not found"}), 404

    _logger.info(
        f"[API] [Get Project] Retrieved project: {project_id} for user: {current_user_id}"
    )
    return project_schema.jsonify(project), 200


@projects.route("/projects/<int:project_id>", methods=["PUT"])
@jwt_required()
def update_project(project_id):
    """Update a specific project by ID"""
    current_user_id = int(get_jwt_identity())
    project = Project.query.get_or_404(project_id)

    if project.creator_id != current_user_id:
        _logger.warning(
            f"[API] [Update Project] Unauthorized access attempt for project: {project_id} by user: {current_user_id}"
        )
        return jsonify({"error": "You are not authorized to edit this project"}), 403

    try:
        data = project_schema.load(request.json, partial=True, unknown=INCLUDE)
    except ValidationError as err:
        msg = f"[API] [Update Project] Validation error during project update: {err.messages}"
        _logger.error(msg)
        return jsonify(err.messages), 400

    for key, value in data.items():
        setattr(project, key, value)

    db.session.commit()
    _logger.info(
        f"[API] [Update Project] Updated project: {project_id} by user: {current_user_id}"
    )
    return project_schema.jsonify(project), 200


@projects.route("/projects/<int:project_id>", methods=["DELETE"])
@jwt_required()
def delete_project(project_id):
    """Delete a specific project by ID"""
    current_user_id = int(get_jwt_identity())
    project = Project.query.get_or_404(project_id)

    if project.creator_id != current_user_id:
        _logger.warning(
            f"[API] [Delete Project] Unauthorized access attempt for project: {project_id} by user: {current_user_id}"
        )
        return jsonify({"error": "You are not authorized to delete this project"}), 403

    db.session.delete(project)
    db.session.commit()
    _logger.info(
        f"[API] [Delete Project] Deleted project: {project_id} by user: {current_user_id}"
    )
    return "", 204
