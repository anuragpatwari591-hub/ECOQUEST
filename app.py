"""EcoQuest Flask application entry point."""
import os
from flask import Flask, render_template, session, redirect, url_for
from config import Config
from utils import database


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    database.init_app(app)

    from routes import auth, student, quiz, challenge, teacher, admin
    app.register_blueprint(auth.bp)
    app.register_blueprint(student.bp)
    app.register_blueprint(quiz.bp)
    app.register_blueprint(challenge.bp)
    app.register_blueprint(teacher.bp)
    app.register_blueprint(admin.bp)

    @app.route("/")
    def index():
        if "user_id" in session:
            role = session.get("role")
            if role == "student":
                return redirect(url_for("student.dashboard"))
            elif role == "teacher":
                return redirect(url_for("teacher.dashboard"))
            elif role == "admin":
                return redirect(url_for("admin.dashboard"))
        return render_template("index.html")

    @app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template("errors/500.html"), 500

    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV", "development") != "production"
    app.run(host="0.0.0.0", port=port, debug=debug)
