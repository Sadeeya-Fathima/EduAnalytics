
import re
from ipaddress import ip_address

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import generate_password_hash

from app.extensions import db
from app.models import Institution, User

from functools import wraps
from threading import Lock

setup_bp = Blueprint("setup", __name__, url_prefix="/setup")

_setup_lock = Lock()


def _serialize_setup_requests(view):
    """Prevent concurrent first-run setup requests within this process."""
    @wraps(view)
    def wrapped(*args, **kwargs):
        with _setup_lock:
            return view(*args, **kwargs)

    return wrapped


def _is_local_request():
    """Allow first-run setup only from a loopback address."""
    try:
        return ip_address(request.remote_addr or "").is_loopback
    except ValueError:
        return False


def _setup_is_complete():
    """Treat any existing user as evidence that setup has already begun."""
    return User.query.first() is not None


@setup_bp.route("/", methods=["GET", "POST"])
@_serialize_setup_requests
def first_run():
    if not _is_local_request():
        abort(403)

    if _setup_is_complete():
        return render_template("setup/complete.html"), 403

    if request.method == "POST":
        institution_name = request.form.get("institution_name", "").strip()
        userid = request.form.get("userid", "").strip()
        email = request.form.get("email", "").strip().lower()
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not all(
            [institution_name, userid, email, first_name, last_name, password]
        ):
            flash("Please complete all required fields.", "error")
            return render_template("setup/first_run.html"), 400

        if len(institution_name) > 150 or len(userid) > 80:
            flash("Institution name or user ID is too long.", "error")
            return render_template("setup/first_run.html"), 400

        if len(email) > 255 or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            flash("Enter a valid email address.", "error")
            return render_template("setup/first_run.html"), 400

        if len(first_name) > 80 or len(last_name) > 80:
            flash("First name or last name is too long.", "error")
            return render_template("setup/first_run.html"), 400

        if len(password) < 8:
            flash("Password must contain at least 8 characters.", "error")
            return render_template("setup/first_run.html"), 400

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return render_template("setup/first_run.html"), 400

        if User.query.filter_by(userid=userid).first():
            flash("That user ID is already in use.", "error")
            return render_template("setup/first_run.html"), 400

        if User.query.filter_by(email=email).first():
            flash("That email address is already in use.", "error")
            return render_template("setup/first_run.html"), 400

        try:
            institution = Institution.query.filter_by(
                name=institution_name
            ).first()

            if institution is None:
                institution = Institution(name=institution_name)
                db.session.add(institution)
                db.session.flush()

            admin = User(
                userid=userid,
                email=email,
                institution_id=institution.id,
                first_name=first_name,
                last_name=last_name,
                title="Administrator",
                role="admin",
                status="active",
                password=generate_password_hash(password),
            )
            db.session.add(admin)
            db.session.commit()

        except SQLAlchemyError:
            db.session.rollback()
            flash("Setup failed. No changes were saved. Please try again.", "error")
            return render_template("setup/first_run.html"), 500

        flash("Initial setup completed. You can now sign in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("setup/first_run.html")
