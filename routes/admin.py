"""Admin dashboard: user/topic/lesson/quiz/challenge/badge management."""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, abort
from utils.database import query_all, query_one, execute
from utils.auth import role_required, hash_password

bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.route("/dashboard")
@role_required("admin")
def dashboard():
    stats = {
        "total_users": query_one("SELECT COUNT(*) AS c FROM users")["c"],
        "students": query_one("SELECT COUNT(*) AS c FROM users WHERE role = 'student'")["c"],
        "teachers": query_one("SELECT COUNT(*) AS c FROM users WHERE role = 'teacher'")["c"],
        "topics": query_one("SELECT COUNT(*) AS c FROM topics")["c"],
        "lessons": query_one("SELECT COUNT(*) AS c FROM lessons")["c"],
        "quizzes": query_one("SELECT COUNT(*) AS c FROM quizzes")["c"],
        "challenges": query_one("SELECT COUNT(*) AS c FROM challenges")["c"],
        "quiz_attempts": query_one("SELECT COUNT(*) AS c FROM quiz_attempts")["c"],
        "challenges_completed": query_one("SELECT COUNT(*) AS c FROM challenge_completions")["c"],
    }
    return render_template("admin/dashboard.html", stats=stats)


@bp.route("/users")
@role_required("admin")
def users():
    rows = query_all(
        "SELECT user_id, name, email, role, class_name, institution, total_xp, created_at "
        "FROM users ORDER BY created_at DESC"
    )
    return render_template("admin/users.html", users=rows)


@bp.route("/users/create", methods=["GET", "POST"])
@role_required("admin")
def create_user():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        role = request.form.get("role", "student")

        if not name or not email or not password:
            flash("Name, email and password are required.", "danger")
            return render_template("admin/create_user.html")

        existing = query_one("SELECT user_id FROM users WHERE email = %s", (email,))
        if existing:
            flash("A user with this email already exists.", "danger")
            return render_template("admin/create_user.html")

        execute(
            "INSERT INTO users (name, email, password_hash, role) VALUES (%s, %s, %s, %s)",
            (name, email, hash_password(password), role),
        )
        flash(f"{role.title()} account created.", "success")
        return redirect(url_for("admin.users"))

    return render_template("admin/create_user.html")


@bp.route("/users/<int:user_id>/delete", methods=["POST"])
@role_required("admin")
def delete_user(user_id):
    if user_id == session["user_id"]:
        flash("You cannot delete your own account.", "danger")
        return redirect(url_for("admin.users"))
    execute("DELETE FROM users WHERE user_id = %s", (user_id,))
    flash("User deleted.", "success")
    return redirect(url_for("admin.users"))


@bp.route("/topics", methods=["GET", "POST"])
@role_required("admin")
def topics():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        icon = request.form.get("icon", "🌱").strip() or "🌱"
        if not name:
            flash("Topic name is required.", "danger")
        else:
            execute(
                "INSERT INTO topics (name, description, icon) VALUES (%s, %s, %s)",
                (name, description, icon),
            )
            flash("Topic created.", "success")

    rows = query_all(
        "SELECT t.*, (SELECT COUNT(*) FROM lessons l WHERE l.topic_id = t.topic_id) AS lesson_count "
        "FROM topics t ORDER BY t.topic_id"
    )
    return render_template("admin/topics.html", topics=rows)


@bp.route("/lessons", methods=["GET", "POST"])
@role_required("admin")
def lessons():
    topics_list = query_all("SELECT * FROM topics ORDER BY name")
    if request.method == "POST":
        topic_id = request.form.get("topic_id")
        title = request.form.get("title", "").strip()
        difficulty = request.form.get("difficulty", "Beginner")
        introduction = request.form.get("introduction", "").strip()
        explanation = request.form.get("explanation", "").strip()
        key_points = request.form.get("key_points", "").strip()
        eco_tip = request.form.get("eco_tip", "").strip()
        xp_reward = request.form.get("xp_reward", 10)

        if not title or not topic_id:
            flash("Title and topic are required.", "danger")
        else:
            execute(
                "INSERT INTO lessons (topic_id, title, difficulty, introduction, explanation, key_points, eco_tip, xp_reward) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (topic_id, title, difficulty, introduction, explanation, key_points, eco_tip, xp_reward),
            )
            flash("Lesson created.", "success")

    rows = query_all(
        "SELECT l.*, t.name AS topic_name FROM lessons l JOIN topics t ON l.topic_id = t.topic_id "
        "ORDER BY l.lesson_id"
    )
    return render_template("admin/lessons.html", lessons=rows, topics=topics_list)


@bp.route("/quizzes")
@role_required("admin")
def quizzes():
    rows = query_all(
        "SELECT q.*, t.name AS topic_name, "
        "(SELECT COUNT(*) FROM questions qq WHERE qq.quiz_id = q.quiz_id) AS question_count "
        "FROM quizzes q JOIN topics t ON q.topic_id = t.topic_id ORDER BY q.quiz_id"
    )
    return render_template("admin/quizzes.html", quizzes=rows)


@bp.route("/challenges", methods=["GET", "POST"])
@role_required("admin")
def challenges():
    if request.method == "POST":
        challenge_id = request.form.get("challenge_id")
        is_active = request.form.get("is_active") == "1"
        execute("UPDATE challenges SET is_active = %s WHERE challenge_id = %s", (is_active, challenge_id))
        flash("Challenge status updated.", "success")

    rows = query_all("SELECT * FROM challenges ORDER BY challenge_id")
    return render_template("admin/challenges.html", challenges=rows)


@bp.route("/badges")
@role_required("admin")
def badges():
    rows = query_all(
        "SELECT b.*, (SELECT COUNT(*) FROM user_badges ub WHERE ub.badge_id = b.badge_id) AS earned_count "
        "FROM badges b ORDER BY b.badge_id"
    )
    return render_template("admin/badges.html", badges=rows)
