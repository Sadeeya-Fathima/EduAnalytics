from pathlib import Path

from sqlalchemy import text
from werkzeug.security import generate_password_hash

from app import create_app
from app.developer import routes
from app.extensions import db
from app.models import Institution, User


def backup_app():
    app = create_app({"TESTING": True, "SECRET_KEY": "test-secret-key", "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:", "WTF_CSRF_ENABLED": False, "EDUANALYTICS_ENV": "development", "EDUANALYTICS_DEV_TOOLS_ENABLED": True})
    with app.app_context():
        institution = Institution(name="Test Institution")
        db.session.add(institution)
        db.session.flush()
        db.session.add(User(userid="DEV001", email="dev@example.com", institution_id=institution.id, first_name="Dev", last_name="User", role="developer", status="active", password=generate_password_hash("secret")))
        db.session.commit()
    return app


def login(client):
    with client.session_transaction() as session:
        session["_user_id"] = "DEV001"
        session["_fresh"] = True


def test_backup_page_lists_verified_metadata(monkeypatch, tmp_path):
    app = backup_app()
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    backup = backup_dir / "Test_2026.db"
    backup.write_bytes(b"backup")
    monkeypatch.setattr(routes, "DEFAULT_BACKUP_DIR", backup_dir)
    monkeypatch.setattr(routes, "inspect_backup", lambda path: {"path": path})
    client = app.test_client()
    login(client)

    response = client.get("/developer/backups", environ_base={"REMOTE_ADDR": "127.0.0.1"})

    assert response.status_code == 200
    assert b"Test_2026.db" in response.data
    assert b"Verified" in response.data


def test_manual_backup_reuses_existing_service_and_audits(monkeypatch, tmp_path):
    app = backup_app()
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    created = backup_dir / "New_Backup.db"

    def fake_create_backup(source, destination):
        created.write_bytes(b"verified backup")
        return created

    monkeypatch.setattr(routes, "DEFAULT_BACKUP_DIR", backup_dir)
    monkeypatch.setattr(routes, "create_backup", fake_create_backup)
    monkeypatch.setattr(routes, "inspect_backup", lambda path: {"path": path})
    client = app.test_client()
    login(client)

    response = client.post("/developer/backups", environ_base={"REMOTE_ADDR": "127.0.0.1"})

    assert response.status_code == 200
    assert b"Verified backup created" in response.data
    with app.app_context():
        assert db.session.execute(text("SELECT COUNT(*) FROM audit_events WHERE action = 'backup_create' AND outcome = 'success'")).scalar() == 1
