from werkzeug.security import generate_password_hash

from app import create_app
from app.extensions import db
from app.models import Institution, User


def dashboard_app(role="developer"):
    app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-secret-key",
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "EDUANALYTICS_ENV": "development",
            "EDUANALYTICS_DEV_TOOLS_ENABLED": True,
        }
    )
    with app.app_context():
        institution = Institution(name="Test Institution")
        db.session.add(institution)
        db.session.flush()
        db.session.add(
            User(
                userid="DEVELOPER001",
                email="developer@example.com",
                institution_id=institution.id,
                first_name="Dev",
                last_name="Eloper",
                role=role,
                status="active",
                password=generate_password_hash("test-password"),
            )
        )
        db.session.commit()
    return app


def login(client, userid="DEVELOPER001"):
    with client.session_transaction() as session:
        session["_user_id"] = userid
        session["_fresh"] = True


def test_developer_can_view_safe_dashboard():
    app = dashboard_app()
    client = app.test_client()
    login(client)

    response = client.get(
        "/developer/",
        environ_base={"REMOTE_ADDR": "127.0.0.1"},
    )

    assert response.status_code == 200
    assert b"Developer dashboard" in response.data
    assert b"Test Institution" not in response.data
    assert b"test-password" not in response.data
    assert b"password" not in response.data.lower()
    assert b"Student records" in response.data


def test_non_developer_cannot_view_dashboard():
    app = dashboard_app(role="educator")
    client = app.test_client()
    login(client)

    response = client.get(
        "/developer/",
        environ_base={"REMOTE_ADDR": "127.0.0.1"},
    )

    assert response.status_code == 403


def test_developer_dashboard_rejects_lan_request():
    app = dashboard_app()
    client = app.test_client()
    login(client)

    response = client.get(
        "/developer/",
        environ_base={"REMOTE_ADDR": "192.168.1.20"},
    )

    assert response.status_code == 403
