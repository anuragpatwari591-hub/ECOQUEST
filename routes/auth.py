"""Registration, login and logout routes."""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from utils.database import query_one, execute
from utils.auth import hash_password, verify_password

bp = Blueprint("auth", __name__)


@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        class_name = request.form.get("class_name", "").strip() or None
        institution = request.form.get("institution", "").strip() or None

        if not name or not email or not password:
            flash("Name, email and password are required.", "danger")
            return render_template("register.html")

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "danger")
            return render_template("register.html")

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template("register.html")

        existing = query_one("SELECT user_id FROM users WHERE email = %s", (email,))
        if existing:
            flash("An account with this email already exists.", "danger")
            return render_template("register.html")

        password_hash = hash_password(password)
        execute(
            "INSERT INTO users (name, email, password_hash, role, class_name, institution) "
            "VALUES (%s, %s, %s, 'student', %s, %s)",
            (name, email, password_hash, class_name, institution),
        )
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = query_one("SELECT * FROM users WHERE email = %s", (email,))

        if user is None or not verify_password(password, user["password_hash"]):
            flash("Invalid email or password.", "danger")
            return render_template("login.html")

        session["user_id"] = user["user_id"]
        session["name"] = user["name"]
        session["role"] = user["role"]

        flash(f"Welcome back, {user['name']}!", "success")
        if user["role"] == "student":
            return redirect(url_for("student.dashboard"))
        elif user["role"] == "teacher":
            return redirect(url_for("teacher.dashboard"))
        else:
            return redirect(url_for("admin.dashboard"))

    return render_template("login.html")


@bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("index"))
