from werkzeug.security import generate_password_hash

from app import create_app
from app.developer.audit import record_audit_event
from app.extensions import db
from app.models import AuditEvent, Institution, User


def audit_app():
    app = create_app({
        "TESTING": True,
        "SECRET_KEY": "test-secret-key",
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "EDUANALYTICS_ENV": "development",
        "EDUANALYTICS_DEV_TOOLS_ENABLED": True,
    })
    with app.app_context():
        institution = Institution(name="Test Institution")
        db.session.add(institution)
        db.session.flush()
        db.session.add(User(
            userid="DEV001", email="dev@example.com", institution_id=institution.id,
            first_name="Dev", last_name="User", role="developer", status="active",
            password=generate_password_hash("test-password"),
        ))
        db.session.commit()
    return app


def login(client):
    with client.session_transaction() as session:
        session["_user_id"] = "DEV001"
        session["_fresh"] = True


def test_audit_event_records_minimal_fields_and_redacts_sensitive_context():
    app = audit_app()
    with app.app_context():
        event = record_audit_event(
            actor_userid="DEV001",
            action="record_view",
            resource="User",
            outcome="success",
            record_reference="DEV001",
            context="password hash should not be logged",
        )
        assert event.id is not None
        saved = db.session.get(AuditEvent, event.id)
        assert saved.actor_userid == "DEV001"
        assert saved.outcome == "success"
        assert saved.context == "Sensitive context redacted."


def test_successful_developer_route_access_is_audited():
    app = audit_app()
    client = app.test_client()
    login(client)
    response = client.get("/developer/", environ_base={"REMOTE_ADDR": "127.0.0.1"})
    assert response.status_code == 200
    with app.app_context():
        event = AuditEvent.query.order_by(AuditEvent.id.desc()).first()
        assert event.action == "developer_access"
        assert event.resource == "dashboard"
        assert event.actor_userid == "DEV001"
        assert event.outcome == "success"


def test_denied_lan_developer_access_is_audited():
    app = audit_app()
    client = app.test_client()
    login(client)
    response = client.get("/developer/", environ_base={"REMOTE_ADDR": "192.168.1.20"})
    assert response.status_code == 403
    with app.app_context():
        event = AuditEvent.query.order_by(AuditEvent.id.desc()).first()
        assert event.resource == "non_loopback_request"
        assert event.outcome == "failure"
