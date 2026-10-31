from werkzeug.security import generate_password_hash

from app import create_app
from app.extensions import db
from app.models import AuditEvent, Institution, User


def ui_app():
    app = create_app({"TESTING": True, "SECRET_KEY": "test-secret-key", "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:", "EDUANALYTICS_ENV": "development", "EDUANALYTICS_DEV_TOOLS_ENABLED": True})
    with app.app_context():
        institution = Institution(name="Test Institution")
        db.session.add(institution)
        db.session.flush()
        db.session.add(User(userid="DEV001", email="dev@example.com", institution_id=institution.id, first_name="Dev", last_name="User", role="developer", status="active", password=generate_password_hash("secret")))
        db.session.add(AuditEvent(actor_userid="DEV001", action="test_action", resource="test", outcome="success", context="safe context"))
        db.session.commit()
    return app


def login(client):
    with client.session_transaction() as session:
        session["_user_id"] = "DEV001"
        session["_fresh"] = True


def test_diagnostics_are_bounded_and_do_not_expose_secrets():
    app = ui_app()
    client = app.test_client()
    login(client)
    response = client.get("/developer/diagnostics", environ_base={"REMOTE_ADDR": "127.0.0.1"})
    assert response.status_code == 200
    assert b"Diagnostics" in response.data
    assert b"test-secret-key" not in response.data
    assert b"SECRET_KEY" not in response.data


def test_audit_log_page_displays_events_and_paginates():
    app = ui_app()
    client = app.test_client()
    login(client)
    response = client.get("/developer/audit-log", environ_base={"REMOTE_ADDR": "127.0.0.1"})
    assert response.status_code == 200
    assert b"test_action" in response.data
    assert b"Audit log" in response.data


def test_maintenance_page_contains_safe_offline_guidance():
    app = ui_app()
    client = app.test_client()
    login(client)
    response = client.get("/developer/maintenance", environ_base={"REMOTE_ADDR": "127.0.0.1"})
    assert response.status_code == 200
    assert b"restore_database.py" in response.data
    assert b"reset_database.py" in response.data
