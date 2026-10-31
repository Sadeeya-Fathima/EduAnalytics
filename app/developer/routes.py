from datetime import datetime
from pathlib import Path
import importlib.metadata
import platform
import sys

from flask import abort, current_app, redirect, render_template, request, url_for
from flask_login import current_user
from sqlalchemy import inspect, text

from app.auth.decorators import developer_access_required
from app.developer import developer_bp
from app.developer.audit import record_audit_event
from app.extensions import db
from app.models import AuditEvent, Dataset, Institution, StudentRecord, UploadError, User
from app.developer.services import RESOURCE_DEFINITIONS, get_resource, serialize_record, update_record
from scripts.backup_database import DEFAULT_BACKUP_DIR, DATABASE_PATH, create_backup
from scripts.restore_database import inspect_backup


def _database_location():
    database_name = db.engine.url.database
    if not database_name or database_name == ":memory:":
        return "in-memory database"
    return str(Path(database_name).resolve())


def _database_integrity():
    result = db.session.execute(text("PRAGMA integrity_check")).scalar()
    return result or "unavailable"


def _latest_backup():
    project_root = Path(current_app.root_path).parent
    backup_dir = project_root.parent / "EduAnalytics_Backups"
    if not backup_dir.is_dir():
        return None

    backups = sorted(
        (path for path in backup_dir.glob("*.db") if path.is_file()),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    if not backups:
        return None

    latest = backups[0]
    return {
        "name": latest.name,
        "created": datetime.fromtimestamp(latest.stat().st_mtime).astimezone(),
        "location": str(backup_dir.resolve()),
    }


@developer_bp.route("/")
@developer_access_required
def dashboard():
    inspector = inspect(db.engine)
    latest_backup = _latest_backup()

    return render_template(
        "developer/dashboard.html",
        environment=current_app.config.get("EDUANALYTICS_ENV"),
        developer_tools_enabled=current_app.config.get(
            "EDUANALYTICS_DEV_TOOLS_ENABLED"
        ),
        database_location=_database_location(),
        database_integrity=_database_integrity(),
        table_count=len(inspector.get_table_names()),
        counts={
            "institutions": Institution.query.count(),
            "users": User.query.count(),
            "datasets": Dataset.query.count(),
            "student_records": StudentRecord.query.count(),
            "upload_errors": UploadError.query.count(),
        },
        latest_backup=latest_backup,
    )


@developer_bp.route("/database")
@developer_access_required
def database_overview():
    return render_template(
        "developer/database.html",
        resources=list(RESOURCE_DEFINITIONS.values()),
    )


@developer_bp.route("/database/tables")
@developer_access_required
def database_tables():
    return database_overview()


@developer_bp.route("/backups", methods=["GET", "POST"])
@developer_access_required
def backups():
    message = None
    error = None
    if request.method == "POST":
        try:
            created = create_backup(DATABASE_PATH, DEFAULT_BACKUP_DIR)
            record_audit_event(actor_userid=current_user.get_id(), action="backup_create", resource="database", outcome="success", record_reference=created.name, context="Verified backup created through existing backup service.")
            message = f"Verified backup created: {created.name}"
        except Exception as exc:
            db.session.rollback()
            record_audit_event(actor_userid=current_user.get_id(), action="backup_create", resource="database", outcome="failure", context="Backup creation failed.")
            error = str(exc)

    backup_rows = []
    if DEFAULT_BACKUP_DIR.is_dir():
        for path in sorted(DEFAULT_BACKUP_DIR.glob("*.db"), key=lambda item: item.stat().st_mtime, reverse=True):
            try:
                inspect_backup(path)
                status = "Verified"
            except Exception:
                status = "Invalid"
            stat = path.stat()
            backup_rows.append({"name": path.name, "created": datetime.fromtimestamp(stat.st_mtime).astimezone().strftime("%Y-%m-%d %H:%M:%S %Z"), "size": f"{stat.st_size / 1024:.1f} KB", "status": status})

    return render_template("developer/backups.html", backups=backup_rows, message=message, error=error)


@developer_bp.route("/diagnostics")
@developer_access_required
def diagnostics():
    dependency_versions = {}
    for package in ("Flask", "Flask-Login", "Flask-SQLAlchemy", "SQLAlchemy", "Werkzeug"):
        try:
            dependency_versions[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            dependency_versions[package] = "not installed"
    return render_template(
        "developer/diagnostics.html",
        python_version=platform.python_version(),
        platform=platform.platform(),
        application_version=current_app.config.get("APP_VERSION", "unversioned"),
        dependency_versions=dependency_versions,
        database_integrity=_database_integrity(),
        tables=sorted(inspect(db.engine).get_table_names()),
        backup_directory=str((Path(current_app.root_path).parent.parent / "EduAnalytics_Backups").resolve()),
    )


@developer_bp.route("/audit-log")
@developer_access_required
def audit_log():
    try:
        page = max(1, int(request.args.get("page", 1)))
    except (TypeError, ValueError):
        page = 1
    pagination = AuditEvent.query.order_by(AuditEvent.id.desc()).paginate(page=page, per_page=25, error_out=False)
    return render_template(
        "developer/audit_log.html",
        events=pagination.items,
        page=pagination.page,
        total_pages=max(1, pagination.pages),
        total=pagination.total,
    )


@developer_bp.route("/maintenance")
@developer_access_required
def maintenance():
    return render_template("developer/maintenance.html")


@developer_bp.route("/database/records/<resource>")
@developer_access_required
def records(resource):
    definition = get_resource(resource)
    if definition is None:
        abort(404)

    try:
        page = max(1, int(request.args.get("page", 1)))
    except (TypeError, ValueError):
        page = 1

    pagination = definition.model.query.order_by(
        *definition.model.__table__.primary_key.columns
    ).paginate(page=page, per_page=25, error_out=False)
    return render_template(
        "developer/records.html",
        resource=definition,
        records=[serialize_record(record, definition) for record in pagination.items],
        page=pagination.page,
        total_pages=max(1, pagination.pages),
        total=pagination.total,
    )


@developer_bp.route("/database/records/<resource>/<record_id>/edit", methods=["GET", "POST"])
@developer_access_required
def edit_record(resource, record_id):
    definition = get_resource(resource)
    if definition is None or not definition.editable_fields:
        abort(404)

    try:
        primary_key = record_id if resource == "users" else int(record_id)
        record = db.session.get(definition.model, primary_key)
    except (TypeError, ValueError):
        record = None
    if record is None:
        abort(404)

    values = serialize_record(record, definition)
    if request.method == "POST":
        submitted = {field: request.form.get(field, "") for field in definition.editable_fields}
        try:
            update_record(definition, record, submitted)
            record_audit_event(actor_userid=current_user.get_id(), action="record_update", resource=resource, outcome="success", record_reference=record_id, context="Allowlisted Developer update.")
        except ValueError as error:
            db.session.rollback()
            record_audit_event(actor_userid=current_user.get_id(), action="record_update", resource=resource, outcome="failure", record_reference=record_id, context=str(error))
            return render_template("developer/edit_record.html", resource=definition, values=submitted, error=str(error)), 400
        return redirect(url_for("developer.records", resource=resource))

    return render_template("developer/edit_record.html", resource=definition, values=values, error=None)
