"""Database-level tests: insertion, retrieval, updates and referential integrity."""
import pymysql
import pytest
from utils.database import query_all, query_one, execute


def test_insertion_and_retrieval(app):
    with app.app_context():
        _, topic_id = execute(
            "INSERT INTO topics (name, description, icon) VALUES (%s, %s, %s)",
            ("Test Topic", "A topic for testing", "🧪"),
        )
        topic = query_one("SELECT * FROM topics WHERE topic_id = %s", (topic_id,))
    assert topic["name"] == "Test Topic"


def test_update(app):
    with app.app_context():
        execute("UPDATE users SET name = %s WHERE user_id = 1", ("Renamed Student",))
        user = query_one("SELECT name FROM users WHERE user_id = 1")
    assert user["name"] == "Renamed Student"


def test_deletion(app):
    with app.app_context():
        _, topic_id = execute(
            "INSERT INTO topics (name, description, icon) VALUES (%s, %s, %s)",
            ("Deletable Topic", "desc", "🗑️"),
        )
        execute("DELETE FROM topics WHERE topic_id = %s", (topic_id,))
        topic = query_one("SELECT * FROM topics WHERE topic_id = %s", (topic_id,))
    assert topic is None


def test_foreign_key_cascade_lesson_to_topic(app):
    """Deleting a topic should cascade-delete its lessons (schema.sql: ON DELETE CASCADE)."""
    with app.app_context():
        lesson_before = query_one("SELECT * FROM lessons WHERE lesson_id = 1")
        assert lesson_before is not None
        execute("DELETE FROM topics WHERE topic_id = 1")
        lesson_after = query_one("SELECT * FROM lessons WHERE lesson_id = 1")
    assert lesson_after is None


def test_unique_constraint_on_user_email(app):
    with app.app_context():
        with pytest.raises(pymysql.err.IntegrityError):
            execute(
                "INSERT INTO users (name, email, password_hash, role) VALUES (%s, %s, %s, %s)",
                ("Dup", "student@test.com", "hash", "student"),
            )


def test_unique_constraint_on_lesson_completion(app):
    with app.app_context():
        execute("INSERT INTO lesson_completions (user_id, lesson_id) VALUES (1, 1)")
        with pytest.raises(pymysql.err.IntegrityError):
            execute("INSERT INTO lesson_completions (user_id, lesson_id) VALUES (1, 1)")


def test_one_to_many_quiz_to_questions(app):
    with app.app_context():
        questions = query_all("SELECT * FROM questions WHERE quiz_id = 1")
    assert len(questions) == 2


def test_one_to_many_question_to_options(app):
    with app.app_context():
        options = query_all("SELECT * FROM options WHERE question_id = 1")
    assert len(options) == 4
    correct = [o for o in options if o["is_correct"]]
    assert len(correct) == 1


def test_leaderboard_sql_orders_by_xp_descending(app):
    with app.app_context():
        execute(
            "INSERT INTO users (name, email, password_hash, role, total_xp) VALUES "
            "('High XP Student', 'high@test.com', 'hash', 'student', 5000)"
        )
        rows = query_all(
            "SELECT name, total_xp FROM users WHERE role = 'student' ORDER BY total_xp DESC"
        )
    assert rows[0]["name"] == "High XP Student"
    assert rows[0]["total_xp"] == 5000
