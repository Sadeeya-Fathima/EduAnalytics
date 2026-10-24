# app/auth/routes.py

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user
from werkzeug.security import check_password_hash

from app.auth import auth_bp
from app.models import User

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    if request.method == "POST":
        userid = request.form.get("userid", "").strip()
        password = request.form.get("password", "")

        user = User.query.filter_by(userid=userid).first()
        if (
            user is None
            or not check_password_hash(user.password, password)
            or user.status != "active"
        ):
            flash("Invalid user ID or password, or account is inactive.", "error")
            return render_template("auth/login.html"), 401
        login_user(user)
        return redirect(url_for("home"))

    return render_template("auth/login.html")

@auth_bp.route("/logout", methods=["POST"])
def logout():
    if current_user.is_authenticated:
        logout_user()
        flash("You have been logged out.", "success")
    return redirect(url_for("auth.login"))