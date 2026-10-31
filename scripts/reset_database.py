"""Safely reset an EduAnalytics development database to first-run state."""

import os
import socket
import sqlite3
import sys
from pathlib import Path

# Direct execution places scripts/ on sys.path; expose the repository root.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app import create_app
from app.extensions import db
from scripts.backup_database import DATABASE_PATH, DEFAULT_BACKUP_DIR, create_backup


CONFIRMATION = "RESET DATABASE"
MAINTENANCE_LOG = PROJECT_ROOT.parent / "EduAnalytics_Maintenance" / "maintenance.log"
REQUIRED_TABLES = {"institution", "users", "datasets", "student_records", "upload_errors", "audit_events"}


def server_appears_running(database_path=DATABASE_PATH):
    project_root = database_path.parent.parent
    if (project_root / ".eduanalytics.pid").exists():
        return True
    try:
        with socket.create_connection(("127.0.0.1", 5000), timeout=1):
            return True
    except OSError:
        return False


def _ensure_not_in_use(database_path):
    if server_appears_running(database_path):
        raise RuntimeError("EduAnalytics may be running. Stop it with .\\stop.ps1 and retry.")
    for suffix in ("-wal", "-shm"):
        if Path(str(database_path) + suffix).exists():
            raise RuntimeError(f"SQLite sidecar file exists: {database_path}{suffix}")
    connection = sqlite3.connect(str(database_path), timeout=5)
    connection.close()


def _verify_empty_database(database_path):
    connection = sqlite3.connect(str(database_path))
    try:
        tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
        missing = REQUIRED_TABLES - tables
        if missing:
            raise RuntimeError(f"Required tables are missing: {sorted(missing)}")
        if connection.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise RuntimeError("Database integrity check failed.")
        for table in ("institution", "users", "datasets", "student_records", "upload_errors", "audit_events"):
            if connection.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0] != 0:
                raise RuntimeError(f"Reset verification found records in {table}.")
    finally:
        connection.close()


def _write_maintenance_event(outcome, database_path, maintenance_log=MAINTENANCE_LOG):
    maintenance_log.parent.mkdir(parents=True, exist_ok=True)
    with maintenance_log.open("a", encoding="utf-8") as handle:
        handle.write(f"database_reset outcome={outcome} database={database_path.name}\n")


def reset_database(database_path=DATABASE_PATH, backup_dir=DEFAULT_BACKUP_DIR, app_factory=create_app, confirmation=None, maintenance_log=MAINTENANCE_LOG):
    if os.environ.get("EDUANALYTICS_ENV", "production") != "development":
        raise RuntimeError("Database reset requires EDUANALYTICS_ENV=development.")
    if os.environ.get("EDUANALYTICS_DEV_TOOLS_ENABLED", "").lower() not in {"1", "true", "yes", "on"}:
        raise RuntimeError("Developer tools must be enabled before database reset.")
    if not database_path.is_file():
        raise FileNotFoundError(f"Database not found: {database_path}")

    _ensure_not_in_use(database_path)
    safety_backup = create_backup(database_path, backup_dir)
    if confirmation != CONFIRMATION:
        return {"reset": False, "safety_backup": safety_backup}

    try:
        database_path.unlink()
        app = app_factory({
            "SECRET_KEY": os.environ.get("SECRET_KEY") or "reset-test-secret",
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{database_path}",
            "EDUANALYTICS_ENV": "development",
            "EDUANALYTICS_DEV_TOOLS_ENABLED": True,
        })
        with app.app_context():
            db.create_all()
        _verify_empty_database(database_path)
        _write_maintenance_event("success", database_path, maintenance_log)
        return {"reset": True, "safety_backup": safety_backup}
    except Exception:
        _write_maintenance_event("failure", database_path, maintenance_log)
        raise


def main():
    print("EduAnalytics - Full Development Database Reset")
    print("WARNING: This removes all application accounts and academic data.")
    print(f"Database: {DATABASE_PATH}")
    confirmation = input(f"Type {CONFIRMATION} to continue: ").strip()
    try:
        result = reset_database(confirmation=confirmation)
        if not result["reset"]:
            print("Reset cancelled. No database changes were made.")
            print(f"Safety backup retained: {result['safety_backup']}")
            return 0
        print("Database reset completed successfully.")
        print(f"Safety backup retained: {result['safety_backup']}")
        print("The application is ready for first-run setup.")
        return 0
    except (FileNotFoundError, OSError, RuntimeError, sqlite3.Error) as exc:
        print(f"ERROR: Database reset failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
