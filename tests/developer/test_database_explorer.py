from werkzeug.security import generate_password_hash

from app import create_app
from app.extensions import db
from app.models import Institution, User


def explorer_app():
    app = create_app({"TESTING": True, "SECRET_KEY": "test-secret-key", "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:", "EDUANALYTICS_ENV": "development", "EDUANALYTICS_DEV_TOOLS_ENABLED": True})
    with app.app_context():
        institution = Institution(name="Test Institution")
        db.session.add(institution)
        db.session.flush()
        db.session.add(User(userid="DEV001", email="dev@example.com", institution_id=institution.id, first_name="Dev", last_name="User", role="developer", status="active", password=generate_password_hash("secret-password")))
        db.session.commit()
    return app


def login(client):
    with client.session_transaction() as session:
        session["_user_id"] = "DEV001"
        session["_fresh"] = True


def test_developer_can_view_allowlisted_resources_and_redacted_fields():
    app = explorer_app()
    client = app.test_client()
    login(client)
    overview = client.get("/developer/database", environ_base={"REMOTE_ADDR": "127.0.0.1"})
    users = client.get("/developer/database/records/users", environ_base={"REMOTE_ADDR": "127.0.0.1"})
    assert overview.status_code == 200
    assert b"Users" in overview.data
    assert users.status_code == 200
    assert b"dev@example.com" in users.data
    assert b"password" not in users.data.lower()
    assert b"secret-password" not in users.data


def test_unknown_resource_is_rejected():
    app = explorer_app()
    client = app.test_client()
    login(client)
    response = client.get("/developer/database/records/users;DROP TABLE users", environ_base={"REMOTE_ADDR": "127.0.0.1"})
    assert response.status_code == 404


def test_records_use_pagination_and_bad_page_defaults_safely():
    app = explorer_app()
    client = app.test_client()
    login(client)
    response = client.get("/developer/database/records/users?page=not-a-number", environ_base={"REMOTE_ADDR": "127.0.0.1"})
    assert response.status_code == 200
    assert b"Page 1 of 1" in response.data


def test_database_explorer_requires_developer_access():
    app = explorer_app()
    response = app.test_client().get("/developer/database", environ_base={"REMOTE_ADDR": "127.0.0.1"})
    assert response.status_code in {302, 401}
