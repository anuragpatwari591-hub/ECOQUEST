"""Student dashboard, topics, lessons, leaderboard and progress routes."""
from datetime import date
from flask import Blueprint, render_template, session, redirect, url_for, flash, abort
from utils.database import query_all, query_one, execute
from utils.auth import role_required
from utils.gamification import calculate_level, xp_for_next_level, award_xp, update_topic_progress

bp = Blueprint("student", __name__, url_prefix="/student")


@bp.route("/dashboard")
@role_required("student")
def dashboard():
    user_id = session["user_id"]
    user = query_one("SELECT * FROM users WHERE user_id = %s", (user_id,))

    level = calculate_level(user["total_xp"])
    xp_needed = xp_for_next_level(user["total_xp"])
    badge_count = query_one(
        "SELECT COUNT(*) AS c FROM user_badges WHERE user_id = %s", (user_id,)
    )["c"]

    progress_rows = query_all(
        "SELECT t.name, t.topic_id, COALESCE(up.progress_percent, 0) AS progress_percent "
        "FROM topics t LEFT JOIN user_progress up ON t.topic_id = up.topic_id AND up.user_id = %s "
        "ORDER BY t.topic_id",
        (user_id,),
    )

    recent_activity = query_all(
        "SELECT activity_type, description, xp_change, created_at FROM activity_log "
        "WHERE user_id = %s ORDER BY created_at DESC LIMIT 5",
        (user_id,),
    )

    rank_row = query_one(
        "SELECT rnk FROM (SELECT user_id, RANK() OVER (ORDER BY total_xp DESC) AS rnk "
        "FROM users WHERE role = 'student') ranked WHERE user_id = %s",
        (user_id,),
    )
    leaderboard_position = rank_row["rnk"] if rank_row else None

    today_challenge = query_one(
        "SELECT * FROM challenges WHERE is_active = TRUE "
        "AND challenge_id NOT IN ("
        "  SELECT challenge_id FROM challenge_completions WHERE user_id = %s AND completed_on = %s"
        ") ORDER BY RAND() LIMIT 1",
        (user_id, date.today()),
    )

    return render_template(
        "student/dashboard.html",
        user=user,
        level=level,
        xp_needed=xp_needed,
        badge_count=badge_count,
        progress_rows=progress_rows,
        recent_activity=recent_activity,
        leaderboard_position=leaderboard_position,
        today_challenge=today_challenge,
    )


@bp.route("/topics")
@role_required("student")
def topics():
    user_id = session["user_id"]
    rows = query_all(
        "SELECT t.*, COALESCE(up.progress_percent, 0) AS progress_percent, "
        "(SELECT COUNT(*) FROM lessons l WHERE l.topic_id = t.topic_id) AS lesson_count "
        "FROM topics t LEFT JOIN user_progress up ON t.topic_id = up.topic_id AND up.user_id = %s "
        "ORDER BY t.topic_id",
        (user_id,),
    )
    return render_template("student/topics.html", topics=rows)


@bp.route("/topics/<int:topic_id>")
@role_required("student")
def topic_detail(topic_id):
    user_id = session["user_id"]
    topic = query_one("SELECT * FROM topics WHERE topic_id = %s", (topic_id,))
    if topic is None:
        abort(404)

    lessons = query_all(
        "SELECT l.*, (lc.completion_id IS NOT NULL) AS is_completed "
        "FROM lessons l LEFT JOIN lesson_completions lc "
        "ON l.lesson_id = lc.lesson_id AND lc.user_id = %s "
        "WHERE l.topic_id = %s ORDER BY l.lesson_id",
        (user_id, topic_id),
    )
    quizzes = query_all("SELECT * FROM quizzes WHERE topic_id = %s", (topic_id,))
    return render_template("student/topic_detail.html", topic=topic, lessons=lessons, quizzes=quizzes)


@bp.route("/lessons/<int:lesson_id>")
@role_required("student")
def lesson_detail(lesson_id):
    user_id = session["user_id"]
    lesson = query_one(
        "SELECT l.*, t.name AS topic_name, "
        "(lc.completion_id IS NOT NULL) AS is_completed "
        "FROM lessons l JOIN topics t ON l.topic_id = t.topic_id "
        "LEFT JOIN lesson_completions lc ON l.lesson_id = lc.lesson_id AND lc.user_id = %s "
        "WHERE l.lesson_id = %s",
        (user_id, lesson_id),
    )
    if lesson is None:
        abort(404)
    return render_template("student/lesson_detail.html", lesson=lesson)


@bp.route("/lessons/<int:lesson_id>/complete", methods=["POST"])
@role_required("student")
def complete_lesson(lesson_id):
    user_id = session["user_id"]
    lesson = query_one("SELECT * FROM lessons WHERE lesson_id = %s", (lesson_id,))
    if lesson is None:
        abort(404)

    already_done = query_one(
        "SELECT completion_id FROM lesson_completions WHERE user_id = %s AND lesson_id = %s",
        (user_id, lesson_id),
    )
    if already_done:
        flash("You have already completed this lesson.", "info")
        return redirect(url_for("student.lesson_detail", lesson_id=lesson_id))

    execute(
        "INSERT INTO lesson_completions (user_id, lesson_id) VALUES (%s, %s)",
        (user_id, lesson_id),
    )
    update_topic_progress(user_id, lesson["topic_id"])
    new_badges = award_xp(
        user_id, lesson["xp_reward"], "lesson_completed", f"Completed lesson: {lesson['title']}"
    )

    flash(f"Lesson completed! +{lesson['xp_reward']} XP", "success")
    for badge in new_badges:
        flash(f"Badge unlocked: {badge['icon']} {badge['name']}!", "success")

    return redirect(url_for("student.topic_detail", topic_id=lesson["topic_id"]))


@bp.route("/leaderboard")
@role_required("student")
def leaderboard():
    class_filter = query_one("SELECT class_name FROM users WHERE user_id = %s", (session["user_id"],))
    rows = query_all(
        "SELECT user_id, name, class_name, total_xp, "
        "RANK() OVER (ORDER BY total_xp DESC) AS rnk, "
        "(SELECT COUNT(*) FROM user_badges ub WHERE ub.user_id = users.user_id) AS badge_count "
        "FROM users WHERE role = 'student' ORDER BY total_xp DESC LIMIT 50"
    )
    for row in rows:
        row["level"] = calculate_level(row["total_xp"])
    return render_template("student/leaderboard.html", rows=rows, my_class=class_filter["class_name"] if class_filter else None)


@bp.route("/progress")
@role_required("student")
def progress():
    user_id = session["user_id"]
    progress_rows = query_all(
        "SELECT t.name, t.icon, COALESCE(up.progress_percent, 0) AS progress_percent, "
        "COALESCE(up.lessons_completed, 0) AS lessons_completed, "
        "COALESCE(up.total_lessons, (SELECT COUNT(*) FROM lessons l WHERE l.topic_id = t.topic_id)) AS total_lessons "
        "FROM topics t LEFT JOIN user_progress up ON t.topic_id = up.topic_id AND up.user_id = %s "
        "ORDER BY t.topic_id",
        (user_id,),
    )
    badges = query_all(
        "SELECT b.name, b.description, b.icon, ub.earned_at FROM user_badges ub "
        "JOIN badges b ON ub.badge_id = b.badge_id WHERE ub.user_id = %s ORDER BY ub.earned_at DESC",
        (user_id,),
    )
    all_badges = query_all("SELECT * FROM badges")
    activity = query_all(
        "SELECT activity_type, description, xp_change, created_at FROM activity_log "
        "WHERE user_id = %s ORDER BY created_at DESC LIMIT 20",
        (user_id,),
    )
    return render_template(
        "student/progress.html", progress_rows=progress_rows, badges=badges,
        all_badges=all_badges, activity=activity,
    )


@bp.route("/profile")
@role_required("student")
def profile():
    user = query_one("SELECT * FROM users WHERE user_id = %s", (session["user_id"],))
    level = calculate_level(user["total_xp"])
    return render_template("student/profile.html", user=user, level=level)
