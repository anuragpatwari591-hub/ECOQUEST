"""Authentication and authorization helpers."""
from functools import wraps
from flask import session, redirect, url_for, flash, abort
from werkzeug.security import generate_password_hash, check_password_hash


def hash_password(plain_password):
    return generate_password_hash(plain_password)


def verify_password(plain_password, password_hash):
    return check_password_hash(password_hash, plain_password)


def login_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("auth.login"))
        return view_func(*args, **kwargs)
    return wrapped


def role_required(*roles):
    """Restrict a view to one or more roles, e.g. @role_required('teacher', 'admin')."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(*args, **kwargs):
            if "user_id" not in session:
                flash("Please log in to continue.", "warning")
                return redirect(url_for("auth.login"))
            if session.get("role") not in roles:
                abort(403)
            return view_func(*args, **kwargs)
        return wrapped
    return decorator
