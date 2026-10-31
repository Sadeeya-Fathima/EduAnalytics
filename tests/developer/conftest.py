from flask import Flask
from flask_login import LoginManager

from app.auth.decorators import developer_access_required


def protected_test_app(role="developer", **config):
    app = Flask(__name__)
    app.config.update(SECRET_KEY="test-secret-key", **config)
    login_manager = LoginManager()
    login_manager.init_app(app)

    class TestUser:
        is_authenticated = True

        def __init__(self, user_role):
            self.role = user_role

        def get_id(self):
            return "developer001"

    @login_manager.user_loader
    def load_user(user_id):
        return (
            TestUser(role)
            if user_id in {"developer001", "educator001"}
            else None
        )

    @app.route("/developer")
    @developer_access_required
    def developer_page():
        return "Developer access granted"

    return app


def login_as_developer(client, user_id="developer001"):
    with client.session_transaction() as session:
        session["_user_id"] = user_id
        session["_fresh"] = True
