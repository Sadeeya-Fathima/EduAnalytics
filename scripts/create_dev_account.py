"""Create one local Developer account for an enabled development install."""

import re
import sys
from getpass import getpass
from pathlib import Path

# Direct execution adds scripts/ to sys.path, so explicitly expose the
# repository root before importing the application package.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy import inspect
from werkzeug.security import generate_password_hash

from app import create_app
from app.extensions import db
from app.models import Institution, User
from app.developer.audit import record_audit_event


MIN_PASSWORD_LENGTH = 8
REQUIRED_TABLES = {"institution", "users"}


def _fail(message):
    print(f"Error: {message}", file=sys.stderr)
    return 1


def _validate_userid(userid):
    if not userid:
        return "User ID cannot be empty."
    if len(userid) > 80:
        return "User ID cannot exceed 80 characters."
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", userid):
        return "User ID may contain only letters, numbers, dots, hyphens, and underscores."
    return None


def _validate_profile(userid, email, first_name, last_name):
    userid_error = _validate_userid(userid)
    if userid_error:
        return userid_error
    if not email or len(email) > 255 or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        return "Enter a valid email address."
    if not first_name or len(first_name) > 80:
        return "First name is required and cannot exceed 80 characters."
    if not last_name or len(last_name) > 80:
        return "Last name is required and cannot exceed 80 characters."
    return None


def _database_is_initialized():
    tables = set(inspect(db.engine).get_table_names())
    if not REQUIRED_TABLES.issubset(tables):
        return False
    return Institution.query.count() == 1


def main():
    app = create_app()

    with app.app_context():
        if app.config.get("EDUANALYTICS_ENV") != "development":
            return _fail("Developer account provisioning requires EDUANALYTICS_ENV=development.")

        if app.config.get("EDUANALYTICS_DEV_TOOLS_ENABLED") is not True:
            return _fail("Developer tools are disabled. Enable them before provisioning an account.")

        if not _database_is_initialized():
            return _fail(
                "The database is not initialized. Complete normal first-run setup before provisioning."
            )

        print("EduAnalytics - Developer Account Setup")
        print("---------------------------------------")

        userid = input("Username: ").strip()
        email = input("Email: ").strip().lower()
        first_name = input("First name: ").strip()
        last_name = input("Last name: ").strip()
        profile_error = _validate_profile(userid, email, first_name, last_name)
        if profile_error:
            return _fail(profile_error)

        if User.query.filter_by(userid=userid).first() is not None:
            return _fail("That user ID already exists. No account was changed.")

        if User.query.filter_by(email=email).first() is not None:
            return _fail("That email address already exists. No account was changed.")

        password = getpass("Password: ")
        confirm_password = getpass("Confirm password: ")

        if len(password) < MIN_PASSWORD_LENGTH:
            return _fail(
                f"Password must contain at least {MIN_PASSWORD_LENGTH} characters."
            )
        if password != confirm_password:
            return _fail("Passwords do not match.")

        institution = Institution.query.order_by(Institution.id).first()

        developer = User(
            userid=userid,
            email=email,
            institution_id=institution.id,
            first_name=first_name,
            last_name=last_name,
            title="Developer",
            role="developer",
            status="active",
            password=generate_password_hash(password),
        )

        try:
            db.session.add(developer)
            db.session.commit()
            record_audit_event(
                actor_userid="local-operator",
                action="developer_account_provisioning",
                resource="User",
                outcome="success",
                record_reference=userid,
                context="Local Developer account created.",
            )
        except Exception:
            db.session.rollback()
            return _fail("Developer account creation failed. No changes were saved.")

        print("\nDeveloper account created successfully.")
        print("You can now sign in to your local EduAnalytics development installation.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
