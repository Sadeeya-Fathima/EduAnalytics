import sqlite3

from app import create_app
from app.extensions import db
from app.models import Institution, User
from scripts import reset_database


def populated_database(tmp_path):
    path = tmp_path / "eduanalytics.db"
    app = create_app({"TESTING": True, "SECRET_KEY": "test-secret", "SQLALCHEMY_DATABASE_URI": f"sqlite:///{path}"})
    with app.app_context():
        institution = Institution(name="Reset Institution")
        db.session.add(institution)
        db.session.flush()
        db.session.add(User(userid="ADMIN", email="admin@example.com", institution_id=institution.id, first_name="Admin", last_name="User", role="admin", status="active", password="hash"))
        db.session.commit()
        db.engine.dispose()
    return path


def test_reset_requires_development_configuration(monkeypatch, tmp_path):
    path = populated_database(tmp_path)
    monkeypatch.delenv("EDUANALYTICS_ENV", raising=False)
    monkeypatch.setenv("EDUANALYTICS_DEV_TOOLS_ENABLED", "true")
    try:
        reset_database.reset_database(path, tmp_path / "backups", confirmation=reset_database.CONFIRMATION)
    except RuntimeError as error:
        assert "development" in str(error)
    else:
        raise AssertionError("Reset should require development configuration")


def test_reset_cancellation_creates_safety_backup_without_changes(monkeypatch, tmp_path):
    path = populated_database(tmp_path)
    backup_dir = tmp_path / "backups"
    monkeypatch.setenv("EDUANALYTICS_ENV", "development")
    monkeypatch.setenv("EDUANALYTICS_DEV_TOOLS_ENABLED", "true")
    monkeypatch.setattr(reset_database, "server_appears_running", lambda database_path: False)
    result = reset_database.reset_database(path, backup_dir, confirmation="NO", maintenance_log=tmp_path / "maintenance.log")
    assert result["reset"] is False
    assert result["safety_backup"].is_file()
    with sqlite3.connect(path) as connection:
        assert connection.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 1


def test_reset_recreates_empty_verified_schema_and_preserves_backup(monkeypatch, tmp_path):
    path = populated_database(tmp_path)
    backup_dir = tmp_path / "backups"
    monkeypatch.setenv("EDUANALYTICS_ENV", "development")
    monkeypatch.setenv("EDUANALYTICS_DEV_TOOLS_ENABLED", "true")
    monkeypatch.setattr(reset_database, "server_appears_running", lambda database_path: False)
    result = reset_database.reset_database(path, backup_dir, confirmation=reset_database.CONFIRMATION, maintenance_log=tmp_path / "maintenance.log")
    assert result["reset"] is True
    assert result["safety_backup"].is_file()
    with sqlite3.connect(path) as connection:
        assert connection.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
        assert connection.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0
        assert connection.execute("SELECT COUNT(*) FROM audit_events").fetchone()[0] == 0


def test_reset_refuses_active_server(monkeypatch, tmp_path):
    path = populated_database(tmp_path)
    monkeypatch.setenv("EDUANALYTICS_ENV", "development")
    monkeypatch.setenv("EDUANALYTICS_DEV_TOOLS_ENABLED", "true")
    monkeypatch.setattr(reset_database, "server_appears_running", lambda database_path: True)
    try:
        reset_database.reset_database(path, tmp_path / "backups", confirmation=reset_database.CONFIRMATION)
    except RuntimeError as error:
        assert "running" in str(error)
    else:
        raise AssertionError("Reset should refuse an active server")
