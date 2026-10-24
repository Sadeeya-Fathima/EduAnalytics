# app/admin/routes.py

import logging

from flask import flash, redirect, render_template, request, url_for
from werkzeug.security import generate_password_hash

from app.admin import admin_bp
from app.auth.decorators import role_required
from app.extensions import db
from app.models import Institution, User

logger = logging.getLogger(__name__)

@admin_bp.route("/educators")
@role_required("admin")
def educators():
    educator_list = (
        User.query
        .filter_by(role="educator")
        .order_by(User.first_name, User.last_name)
        .all()
    )
    institutions = Institution.query.order_by(Institution.name).all()

    return render_template(
        "admin/educators.html",
        educators=educator_list,
        institutions=institutions,
    )


@admin_bp.route("/educators/create", methods=["POST"])
@role_required("admin")
def create_educator():
    userid = request.form.get("userid", "").strip()
    email = request.form.get("email", "").strip().lower()
    first_name = request.form.get("first_name", "").strip()
    last_name = request.form.get("last_name", "").strip()
    title = request.form.get("title", "").strip()
    institution_id = request.form.get("institution_id", "").strip()
    password = request.form.get("password", "")
    confirm_password = request.form.get("confirm_password", "")

    if not all([userid, email, first_name, last_name, institution_id, password]):
        flash("Please complete all required fields.", "error")
        return redirect(url_for("admin.educators"))

    if len(password) < 8:
        flash("Password must contain at least 8 characters.", "error")
        return redirect(url_for("admin.educators"))

    if password != confirm_password:
        flash("Passwords do not match.", "error")
        return redirect(url_for("admin.educators"))

    try:
        institution_id = int(institution_id)
    except ValueError:
        flash("Please select a valid institution.", "error")
        return redirect(url_for("admin.educators"))

    institution = db.session.get(Institution, institution_id)
    if institution is None:
        flash("The selected institution does not exist.", "error")
        return redirect(url_for("admin.educators"))

    if User.query.filter_by(userid=userid).first():
        flash("That user ID is already in use.", "error")
        return redirect(url_for("admin.educators"))

    if User.query.filter_by(email=email).first():
        flash("That email address is already in use.", "error")
        return redirect(url_for("admin.educators"))

    educator = User(
        userid=userid,
        email=email,
        institution_id=institution.id,
        first_name=first_name,
        last_name=last_name,
        title=title or None,
        role="educator",
        status="active",
        password=generate_password_hash(password),
    )

    try:
        db.session.add(educator)
        db.session.commit()
    except Exception:
        db.session.rollback()
        logger.exception("Failed to create educator account.")
        flash("Could not create the educator account. Please try again.", "error")
        return redirect(url_for("admin.educators"))

    flash("Educator account created successfully.", "success")
    return redirect(url_for("admin.educators"))


@admin_bp.route(
    "/educators/<userid>/status",
    methods=["POST"],
)
@role_required("admin")
def change_educator_status(userid):
    educator = db.session.get(User, userid)

    if educator is None or educator.role != "educator":
        flash("Educator account not found.", "error")
        return redirect(url_for("admin.educators"))

    new_status = request.form.get("status", "").strip().lower()

    if new_status not in {"active", "inactive"}:
        flash("Invalid account status.", "error")
        return redirect(url_for("admin.educators"))

    educator.status = new_status

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        logger.exception("Failed to update educator account status.")
        flash("Could not update the educator account. Please try again.", "error")
        return redirect(url_for("admin.educators"))

    flash(
        f"Educator account {new_status}.",
        "success",
    )
    return redirect(url_for("admin.educators"))
