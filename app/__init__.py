# app/__init__.py

import os

from flask import Flask, render_template
from werkzeug.exceptions import RequestEntityTooLarge
from flask_wtf.csrf import CSRFProtect
from flask_login import login_required

from app.extensions import db, login_manager

csrf = CSRFProtect()

@login_manager.user_loader
def load_user(user_id):
    """Load only active users from the database."""
    from app.models import User

    user = db.session.get(User, user_id)

    if user is not None and user.status != "active":
        return None

    return user

def create_app(test_config=None):
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///eduanalytics.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

    if test_config:
        app.config.update(test_config)

    if not app.config.get("SECRET_KEY"):
        raise RuntimeError(
            "SECRET_KEY must be set before starting EduAnalytics. "
            "Set it as an environment variable."
        )


    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    csrf.init_app(app)

    @app.errorhandler(RequestEntityTooLarge)
    def handle_upload_too_large(error):
        from flask import flash, redirect, url_for

        flash("This CSV file is too large. Please upload a file no larger than 5 MiB.", "error")
        return redirect(url_for("datasets.upload"))

    from app import models  # Register the models with SQLAlchemy
    from app.auth import auth_bp
    from app.admin import admin_bp
    from app.datasets import datasets_bp
    from app.setup import setup_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(datasets_bp)
    app.register_blueprint(setup_bp)

    with app.app_context():
        db.create_all()

    @app.route("/")
    @login_required
    def home():
        return render_template("home.html")

    return app
