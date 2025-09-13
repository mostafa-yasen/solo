from extensions import db
from datetime import datetime, timezone


class ProjectMember(db.Model):
    __tablename__ = "project_members"
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), index=True)
    joined_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True)
    description = db.Column(db.Text)
    status = db.Column(db.String(32), default="Active")
    created_at = db.Column(
        db.DateTime,
        default=datetime.now(timezone.utc),
    )
    updated_at = db.Column(
        db.DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )

    creator_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    creator = db.relationship(
        "User",
        backref=db.backref("created_projects", lazy="dynamic"),
    )

    members = db.relationship(
        "User",
        secondary="project_members",
        backref=db.backref("projects", lazy="dynamic"),
    )

    def __repr__(self):
        return f"<Project {self.name}>"
