"""Tests for the quiz module: navigation, scoring, XP and DB persistence."""
from utils.database import query_all, query_one


def test_all_correct_answers_gives_perfect_score(student_client):
    student_client.get("/quiz/1/start")
    response = None
    # Q1 correct option is 1, Q2 correct option is 5
    for opt in ["1", "5"]:
        resp = student_client.get("/quiz/question")
        import re
        qid = re.search(r'name="question_id" value="(\d+)"', resp.data.decode()).group(1)
        response = student_client.post("/quiz/question", data={"question_id": qid, "option_id": opt}, follow_redirects=True)
    assert b"2/2" in response.data
    assert b"Perfect Score Bonus" in response.data


def test_incorrect_answer_reduces_score(student_client):
    student_client.get("/quiz/1/start")
    import re
    response = None
    # Answer Q1 wrong (option 2), Q2 correct (option 5)
    for opt in ["2", "5"]:
        resp = student_client.get("/quiz/question")
        qid = re.search(r'name="question_id" value="(\d+)"', resp.data.decode()).group(1)
        response = student_client.post("/quiz/question", data={"question_id": qid, "option_id": opt}, follow_redirects=True)
    assert b"1/2" in response.data
    assert b"Perfect Score Bonus" not in response.data


def test_xp_calculation_matches_correct_answer_count(app, student_client):
    student_client.get("/quiz/1/start")
    import re
    for opt in ["2", "5"]:  # 1 correct answer -> 10 XP, no perfect bonus
        resp = student_client.get("/quiz/question")
        qid = re.search(r'name="question_id" value="(\d+)"', resp.data.decode()).group(1)
        student_client.post("/quiz/question", data={"question_id": qid, "option_id": opt}, follow_redirects=True)

    with app.app_context():
        attempt = query_one("SELECT * FROM quiz_attempts WHERE user_id = 1 ORDER BY attempt_id DESC LIMIT 1")
    assert attempt["score"] == 1
    assert attempt["xp_earned"] == 10


def test_perfect_quiz_awards_bonus_xp(app, student_client):
    student_client.get("/quiz/1/start")
    import re
    for opt in ["1", "5"]:
        resp = student_client.get("/quiz/question")
        qid = re.search(r'name="question_id" value="(\d+)"', resp.data.decode()).group(1)
        student_client.post("/quiz/question", data={"question_id": qid, "option_id": opt}, follow_redirects=True)

    with app.app_context():
        attempt = query_one("SELECT * FROM quiz_attempts WHERE user_id = 1 ORDER BY attempt_id DESC LIMIT 1")
    # 2 correct * 10 XP + 50 perfect bonus = 70
    assert attempt["xp_earned"] == 70


def test_quiz_attempt_and_answers_stored_in_database(app, student_client):
    student_client.get("/quiz/1/start")
    import re
    for opt in ["1", "2"]:
        resp = student_client.get("/quiz/question")
        qid = re.search(r'name="question_id" value="(\d+)"', resp.data.decode()).group(1)
        student_client.post("/quiz/question", data={"question_id": qid, "option_id": opt}, follow_redirects=True)

    with app.app_context():
        attempt = query_one("SELECT * FROM quiz_attempts WHERE user_id = 1")
        answers = query_all("SELECT * FROM quiz_answers WHERE attempt_id = %s", (attempt["attempt_id"],))
    assert attempt is not None
    assert len(answers) == 2


def test_student_xp_increases_after_quiz(app, student_client):
    with app.app_context():
        xp_before = query_one("SELECT total_xp FROM users WHERE user_id = 1")["total_xp"]

    student_client.get("/quiz/1/start")
    import re
    for opt in ["1", "5"]:
        resp = student_client.get("/quiz/question")
        qid = re.search(r'name="question_id" value="(\d+)"', resp.data.decode()).group(1)
        student_client.post("/quiz/question", data={"question_id": qid, "option_id": opt}, follow_redirects=True)

    with app.app_context():
        xp_after = query_one("SELECT total_xp FROM users WHERE user_id = 1")["total_xp"]
    assert xp_after == xp_before + 70
