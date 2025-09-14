import os

from flask import Flask
from extensions import db, migrate, jwt, ma
from users import users
from projects import projects
from projects.models import Project, ProjectMember
from dotenv import load_dotenv

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "app.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "DEFAULT_JWT_SECRET_KEY")

db.init_app(app)
migrate.init_app(app, db)
jwt.init_app(app)
ma.init_app(app)

app.register_blueprint(users)
app.register_blueprint(projects)


@app.route("/")
def index():
    return "Welcome to Solo. The Project management app"
