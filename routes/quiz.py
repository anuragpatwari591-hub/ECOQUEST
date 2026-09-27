"""Quiz listing, taking, scoring and history."""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, abort
from utils.database import query_all, query_one, execute
from utils.auth import role_required
from utils.gamification import award_xp

bp = Blueprint("quiz", __name__, url_prefix="/quiz")


@bp.route("/")
@role_required("student")
def list_quizzes():
    user_id = session["user_id"]
    quizzes = query_all(
        "SELECT q.*, t.name AS topic_name, "
        "(SELECT COUNT(*) FROM questions qq WHERE qq.quiz_id = q.quiz_id) AS question_count, "
        "(SELECT COUNT(*) FROM quiz_attempts qa WHERE qa.quiz_id = q.quiz_id AND qa.user_id = %s) AS attempt_count "
        "FROM quizzes q JOIN topics t ON q.topic_id = t.topic_id ORDER BY q.quiz_id",
        (user_id,),
    )
    return render_template("student/quiz_list.html", quizzes=quizzes)


@bp.route("/<int:quiz_id>/start")
@role_required("student")
def start_quiz(quiz_id):
    quiz = query_one("SELECT * FROM quizzes WHERE quiz_id = %s", (quiz_id,))
    if quiz is None:
        abort(404)

    questions = query_all(
        "SELECT question_id, question_text FROM questions WHERE quiz_id = %s ORDER BY question_id",
        (quiz_id,),
    )
    if not questions:
        flash("This quiz has no questions yet.", "warning")
        return redirect(url_for("quiz.list_quizzes"))

    # Track progress through the quiz in the session (simple, understandable state)
    session["quiz_state"] = {
        "quiz_id": quiz_id,
        "question_ids": [q["question_id"] for q in questions],
        "current_index": 0,
        "answers": {},  # question_id (str) -> selected_option_id
    }
    return redirect(url_for("quiz.show_question"))


@bp.route("/question", methods=["GET", "POST"])
@role_required("student")
def show_question():
    state = session.get("quiz_state")
    if not state:
        flash("Please start a quiz first.", "warning")
        return redirect(url_for("quiz.list_quizzes"))

    if request.method == "POST":
        question_id = request.form.get("question_id")
        selected_option_id = request.form.get("option_id")
        if selected_option_id:
            state["answers"][question_id] = int(selected_option_id)
        state["current_index"] += 1
        session["quiz_state"] = state
        session.modified = True

        if state["current_index"] >= len(state["question_ids"]):
            return redirect(url_for("quiz.submit_quiz"))
        return redirect(url_for("quiz.show_question"))

    index = state["current_index"]
    if index >= len(state["question_ids"]):
        return redirect(url_for("quiz.submit_quiz"))

    question_id = state["question_ids"][index]
    question = query_one("SELECT * FROM questions WHERE question_id = %s", (question_id,))
    options = query_all(
        "SELECT option_id, option_text FROM options WHERE question_id = %s ORDER BY option_id",
        (question_id,),
    )
    quiz = query_one("SELECT * FROM quizzes WHERE quiz_id = %s", (state["quiz_id"],))

    return render_template(
        "student/quiz_question.html",
        quiz=quiz, question=question, options=options,
        current=index + 1, total=len(state["question_ids"]),
    )


@bp.route("/submit")
@role_required("student")
def submit_quiz():
    state = session.pop("quiz_state", None)
    if not state:
        flash("No active quiz to submit.", "warning")
        return redirect(url_for("quiz.list_quizzes"))

    user_id = session["user_id"]
    quiz_id = state["quiz_id"]
    question_ids = state["question_ids"]
    answers = state["answers"]

    correct_count = 0
    answer_rows = []
    for qid in question_ids:
        selected_option_id = answers.get(str(qid))
        is_correct = False
        if selected_option_id:
            option = query_one(
                "SELECT is_correct FROM options WHERE option_id = %s AND question_id = %s",
                (selected_option_id, qid),
            )
            is_correct = bool(option and option["is_correct"])
        if is_correct:
            correct_count += 1
        answer_rows.append((qid, selected_option_id, is_correct))

    total_questions = len(question_ids)
    xp_earned = correct_count * 10
    is_perfect = correct_count == total_questions
    if is_perfect:
        xp_earned += 50

    _, attempt_id = execute(
        "INSERT INTO quiz_attempts (user_id, quiz_id, score, total_questions, xp_earned) "
        "VALUES (%s, %s, %s, %s, %s)",
        (user_id, quiz_id, correct_count, total_questions, xp_earned),
    )

    for qid, selected_option_id, is_correct in answer_rows:
        execute(
            "INSERT INTO quiz_answers (attempt_id, question_id, selected_option_id, is_correct) "
            "VALUES (%s, %s, %s, %s)",
            (attempt_id, qid, selected_option_id, is_correct),
        )

    quiz = query_one("SELECT title FROM quizzes WHERE quiz_id = %s", (quiz_id,))
    new_badges = award_xp(
        user_id, xp_earned, "quiz_attempted",
        f"Attempted {quiz['title']} - Score {correct_count}/{total_questions}",
    )

    return render_template(
        "student/quiz_result.html",
        score=correct_count, total=total_questions, xp_earned=xp_earned,
        is_perfect=is_perfect, quiz=quiz, new_badges=new_badges,
        accuracy=round((correct_count / total_questions) * 100) if total_questions else 0,
        attempt_id=attempt_id,
    )


@bp.route("/history")
@role_required("student")
def history():
    user_id = session["user_id"]
    attempts = query_all(
        "SELECT qa.*, q.title AS quiz_title FROM quiz_attempts qa "
        "JOIN quizzes q ON qa.quiz_id = q.quiz_id "
        "WHERE qa.user_id = %s ORDER BY qa.attempted_at DESC",
        (user_id,),
    )
    return render_template("student/quiz_history.html", attempts=attempts)


@bp.route("/review/<int:attempt_id>")
@role_required("student")
def review(attempt_id):
    user_id = session["user_id"]
    attempt = query_one(
        "SELECT qa.*, q.title AS quiz_title FROM quiz_attempts qa "
        "JOIN quizzes q ON qa.quiz_id = q.quiz_id "
        "WHERE qa.attempt_id = %s AND qa.user_id = %s",
        (attempt_id, user_id),
    )
    if attempt is None:
        abort(404)

    answers = query_all(
        "SELECT qq.question_text, o.option_text AS selected_text, ans.is_correct, "
        "(SELECT option_text FROM options WHERE question_id = qq.question_id AND is_correct = TRUE) AS correct_text "
        "FROM quiz_answers ans "
        "JOIN questions qq ON ans.question_id = qq.question_id "
        "LEFT JOIN options o ON ans.selected_option_id = o.option_id "
        "WHERE ans.attempt_id = %s",
        (attempt_id,),
    )
    return render_template("student/quiz_review.html", attempt=attempt, answers=answers)
