# app/__init__.py

import os

from flask import Flask, render_template
from werkzeug.exceptions import RequestEntityTooLarge
from flask_wtf.csrf import CSRFProtect, CSRFError
from flask_login import current_user, login_required

from app.extensions import db, login_manager

csrf = CSRFProtect()


def _env_flag(name, default=False):
    """Read a boolean environment flag using an explicit allowlist."""
    value = os.environ.get(name)
    if value is None:
        return default

    return value.strip().lower() in {"1", "true", "yes", "on"}

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
    app.config["EDUANALYTICS_ENV"] = os.environ.get(
        "EDUANALYTICS_ENV", "production"
    )
    app.config["EDUANALYTICS_DEV_TOOLS_ENABLED"] = _env_flag(
        "EDUANALYTICS_DEV_TOOLS_ENABLED", default=False
    )
    app.config["EDUANALYTICS_DEV_TOOLS_LOCAL_ONLY"] = _env_flag(
        "EDUANALYTICS_DEV_TOOLS_LOCAL_ONLY", default=True
    )

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

    @app.errorhandler(403)
    def handle_forbidden(error):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def handle_not_found(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        return render_template("errors/405.html"), 405

    @app.errorhandler(CSRFError)
    def handle_csrf_error(error):
        return render_template("errors/400.html", message="This form has expired. Refresh the page and try again."), 400

    from app import models  # Register the models with SQLAlchemy
    from app.auth import auth_bp
    from app.admin import admin_bp
    from app.datasets import datasets_bp
    from app.analytics import analytics_bp
    from app.developer import developer_bp
    from app.setup import setup_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(datasets_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(developer_bp)
    app.register_blueprint(setup_bp)

    with app.app_context():
        db.create_all()

    @app.route("/")
    @login_required
    def home():
        from app.datasets.routes import accessible_datasets_for_current_user
        from app.models import Dataset, StudentRecord, User

        dataset_query = accessible_datasets_for_current_user()
        dataset_count = dataset_query.count()
        datasets = dataset_query.limit(6).all()
        faculty_count = User.query.filter_by(institution_id=current_user.institution_id, role="educator", status="active").count()
        student_count = (
            db.session.query(db.func.count(StudentRecord.student))
            .join(StudentRecord.dataset)
            .join(Dataset.uploader)
            .filter(User.institution_id == current_user.institution_id)
            .scalar()
            or 0
        )
        return render_template("home.html", datasets=datasets, dataset_count=dataset_count, faculty_count=faculty_count, student_count=student_count)

    return app
