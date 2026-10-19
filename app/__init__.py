
from flask import Flask

from app.extensions import db


def create_app(test_config=None):
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///eduanalytics.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    if test_config:
        app.config.update(test_config)

    db.init_app(app)

    from app import models  # Register the models with SQLAlchemy

    with app.app_context():
        db.create_all()

    @app.route("/")
    def home():
        return "EduAnalytics is running!"

    return app
