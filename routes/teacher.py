"""Teacher dashboard: student performance, quiz/question/challenge authoring."""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, abort
from utils.database import query_all, query_one, execute
from utils.auth import role_required
from utils.gamification import calculate_level

bp = Blueprint("teacher", __name__, url_prefix="/teacher")


@bp.route("/dashboard")
@role_required("teacher")
def dashboard():
    total_students = query_one("SELECT COUNT(*) AS c FROM users WHERE role = 'student'")["c"]
    active_students = query_one(
        "SELECT COUNT(DISTINCT user_id) AS c FROM activity_log "
        "WHERE activity_date >= CURDATE() - INTERVAL 7 DAY"
    )["c"]
    avg_score_row = query_one(
        "SELECT AVG(score / total_questions * 100) AS avg_pct FROM quiz_attempts WHERE total_questions > 0"
    )
    avg_score = round(avg_score_row["avg_pct"], 1) if avg_score_row["avg_pct"] else 0
    quiz_attempts = query_one("SELECT COUNT(*) AS c FROM quiz_attempts")["c"]
    challenges_completed = query_one("SELECT COUNT(*) AS c FROM challenge_completions")["c"]

    topic_completion = query_all(
        "SELECT t.name, ROUND(AVG(COALESCE(up.progress_percent, 0)), 1) AS avg_progress "
        "FROM topics t LEFT JOIN user_progress up ON t.topic_id = up.topic_id "
        "GROUP BY t.topic_id, t.name ORDER BY t.topic_id"
    )

    quiz_performance = query_all(
        "SELECT q.title, ROUND(AVG(qa.score / qa.total_questions * 100), 1) AS avg_pct, COUNT(*) AS attempts "
        "FROM quizzes q LEFT JOIN quiz_attempts qa ON q.quiz_id = qa.quiz_id "
        "GROUP BY q.quiz_id, q.title ORDER BY q.quiz_id"
    )

    return render_template(
        "teacher/dashboard.html",
        total_students=total_students, active_students=active_students,
        avg_score=avg_score, quiz_attempts=quiz_attempts,
        challenges_completed=challenges_completed,
        topic_completion=topic_completion, quiz_performance=quiz_performance,
    )


@bp.route("/students")
@role_required("teacher")
def students():
    rows = query_all(
        "SELECT user_id, name, email, class_name, total_xp, current_streak, "
        "(SELECT COUNT(*) FROM user_badges ub WHERE ub.user_id = users.user_id) AS badge_count "
        "FROM users WHERE role = 'student' ORDER BY total_xp DESC"
    )
    for row in rows:
        row["level"] = calculate_level(row["total_xp"])
    return render_template("teacher/students.html", students=rows)


@bp.route("/students/<int:student_id>")
@role_required("teacher")
def student_detail(student_id):
    student = query_one("SELECT * FROM users WHERE user_id = %s AND role = 'student'", (student_id,))
    if student is None:
        abort(404)
    student["level"] = calculate_level(student["total_xp"])

    quiz_attempts = query_all(
        "SELECT qa.*, q.title AS quiz_title FROM quiz_attempts qa "
        "JOIN quizzes q ON qa.quiz_id = q.quiz_id WHERE qa.user_id = %s ORDER BY qa.attempted_at DESC",
        (student_id,),
    )
    challenge_completions = query_all(
        "SELECT cc.*, c.title FROM challenge_completions cc "
        "JOIN challenges c ON cc.challenge_id = c.challenge_id "
        "WHERE cc.user_id = %s ORDER BY cc.completed_on DESC",
        (student_id,),
    )
    progress = query_all(
        "SELECT t.name, COALESCE(up.progress_percent, 0) AS progress_percent "
        "FROM topics t LEFT JOIN user_progress up ON t.topic_id = up.topic_id AND up.user_id = %s "
        "ORDER BY t.topic_id",
        (student_id,),
    )
    return render_template(
        "teacher/student_detail.html", student=student, quiz_attempts=quiz_attempts,
        challenge_completions=challenge_completions, progress=progress,
    )


@bp.route("/quizzes")
@role_required("teacher")
def quizzes():
    rows = query_all(
        "SELECT q.*, t.name AS topic_name, "
        "(SELECT COUNT(*) FROM questions qq WHERE qq.quiz_id = q.quiz_id) AS question_count "
        "FROM quizzes q JOIN topics t ON q.topic_id = t.topic_id ORDER BY q.quiz_id"
    )
    return render_template("teacher/quizzes.html", quizzes=rows)


@bp.route("/quizzes/create", methods=["GET", "POST"])
@role_required("teacher")
def create_quiz():
    topics = query_all("SELECT * FROM topics ORDER BY name")
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        topic_id = request.form.get("topic_id")

        if not title or not topic_id:
            flash("Title and topic are required.", "danger")
            return render_template("teacher/create_quiz.html", topics=topics)

        _, quiz_id = execute(
            "INSERT INTO quizzes (topic_id, title, description, created_by) VALUES (%s, %s, %s, %s)",
            (topic_id, title, description, session["user_id"]),
        )
        flash("Quiz created. Now add at least one question.", "success")
        return redirect(url_for("teacher.add_question", quiz_id=quiz_id))

    return render_template("teacher/create_quiz.html", topics=topics)


@bp.route("/quizzes/<int:quiz_id>/add-question", methods=["GET", "POST"])
@role_required("teacher")
def add_question(quiz_id):
    quiz = query_one("SELECT * FROM quizzes WHERE quiz_id = %s", (quiz_id,))
    if quiz is None:
        abort(404)

    if request.method == "POST":
        question_text = request.form.get("question_text", "").strip()
        options = [request.form.get(f"option_{i}", "").strip() for i in range(1, 5)]
        correct_index = request.form.get("correct_option")

        if not question_text or not all(options) or correct_index is None:
            flash("Question text and all 4 options (with one marked correct) are required.", "danger")
        else:
            _, question_id = execute(
                "INSERT INTO questions (quiz_id, question_text) VALUES (%s, %s)",
                (quiz_id, question_text),
            )
            for i, option_text in enumerate(options, start=1):
                is_correct = str(i) == correct_index
                execute(
                    "INSERT INTO options (question_id, option_text, is_correct) VALUES (%s, %s, %s)",
                    (question_id, option_text, is_correct),
                )
            flash("Question added.", "success")

    existing_questions = query_all(
        "SELECT question_id, question_text FROM questions WHERE quiz_id = %s ORDER BY question_id",
        (quiz_id,),
    )
    return render_template("teacher/add_question.html", quiz=quiz, existing_questions=existing_questions)


@bp.route("/challenges", methods=["GET", "POST"])
@role_required("teacher")
def challenges():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        category = request.form.get("category", "").strip()
        difficulty = request.form.get("difficulty", "Easy")
        xp_reward = request.form.get("xp_reward", 20)

        if not title:
            flash("Title is required.", "danger")
        else:
            execute(
                "INSERT INTO challenges (title, description, category, difficulty, xp_reward, created_by) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                (title, description, category, difficulty, xp_reward, session["user_id"]),
            )
            flash("Challenge created.", "success")

    rows = query_all(
        "SELECT c.*, (SELECT COUNT(*) FROM challenge_completions cc WHERE cc.challenge_id = c.challenge_id) AS completion_count "
        "FROM challenges c ORDER BY c.challenge_id"
    )
    return render_template("teacher/challenges.html", challenges=rows)
