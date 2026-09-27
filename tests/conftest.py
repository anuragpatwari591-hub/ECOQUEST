"""Pytest fixtures: a real MySQL test database is reset before every test
function so each test runs against clean, known data. This mirrors the
production database engine (MySQL) rather than mocking it, so the SQL in
utils/database.py and the route modules is exercised for real.
"""
import os
import sys
import pathlib
from datetime import date

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from config import TestConfig
from app import create_app
from utils.auth import hash_password

SCHEMA_PATH = pathlib.Path(__file__).resolve().parent.parent / "database" / "schema.sql"


def _run_sql_script(cursor, sql_text, database_name):
    """Execute a .sql file's statements one by one (simple ';' split, which
    is safe here because none of our seed/schema text contains embedded
    semicolons)."""
    for statement in sql_text.split(";"):
        statement = statement.strip()
        if not statement:
            continue
        if statement.upper().startswith("CREATE DATABASE") or statement.upper().startswith("USE "):
            continue
        cursor.execute(statement)


@pytest.fixture()
def app():
    app = create_app(TestConfig)
    with app.app_context():
        from utils.database import get_db
        db = get_db()
        with db.cursor() as cur:
            cur.execute("SET FOREIGN_KEY_CHECKS = 0")
            for table in [
                "quiz_answers", "quiz_attempts", "lesson_completions", "challenge_completions",
                "user_badges", "user_progress", "activity_log", "options", "questions",
                "quizzes", "lessons", "challenges", "badges", "topics", "users",
            ]:
                cur.execute(f"DROP TABLE IF EXISTS {table}")
            cur.execute("SET FOREIGN_KEY_CHECKS = 1")

        schema_sql = SCHEMA_PATH.read_text()
        with db.cursor() as cur:
            _run_sql_script(cur, schema_sql, TestConfig.DB_NAME)

        _seed_minimal_fixture(db)
    yield app


def _seed_minimal_fixture(db):
    """Insert a small, deterministic dataset covering every module under test."""
    with db.cursor() as cur:
        # Users: 1 student, 1 teacher, 1 admin
        cur.execute(
            "INSERT INTO users (user_id, name, email, password_hash, role, total_xp, current_streak, longest_streak, last_activity_date) "
            "VALUES (1, 'Test Student', 'student@test.com', %s, 'student', 90, 0, 0, NULL)",
            (hash_password("password123"),),
        )
        cur.execute(
            "INSERT INTO users (user_id, name, email, password_hash, role) VALUES (2, 'Test Teacher', 'teacher@test.com', %s, 'teacher')",
            (hash_password("password123"),),
        )
        cur.execute(
            "INSERT INTO users (user_id, name, email, password_hash, role) VALUES (3, 'Test Admin', 'admin@test.com', %s, 'admin')",
            (hash_password("password123"),),
        )

        # Topic + lesson
        cur.execute("INSERT INTO topics (topic_id, name, description, icon) VALUES (1, 'Climate Change', 'desc', '🌍')")
        cur.execute(
            "INSERT INTO lessons (lesson_id, topic_id, title, difficulty, introduction, explanation, key_points, eco_tip, xp_reward) "
            "VALUES (1, 1, 'Test Lesson', 'Beginner', 'intro', 'explain', 'point1\\npoint2', 'tip', 10)"
        )

        # Quiz with 2 questions, 4 options each (option A always correct)
        cur.execute("INSERT INTO quizzes (quiz_id, topic_id, title, description, created_by) VALUES (1, 1, 'Test Quiz', 'desc', 2)")
        cur.execute("INSERT INTO questions (question_id, quiz_id, question_text) VALUES (1, 1, 'Question 1?')")
        cur.execute("INSERT INTO questions (question_id, quiz_id, question_text) VALUES (2, 1, 'Question 2?')")
        cur.execute(
            "INSERT INTO options (option_id, question_id, option_text, is_correct) VALUES "
            "(1, 1, 'Correct A', TRUE), (2, 1, 'Wrong B', FALSE), (3, 1, 'Wrong C', FALSE), (4, 1, 'Wrong D', FALSE),"
            "(5, 2, 'Correct A', TRUE), (6, 2, 'Wrong B', FALSE), (7, 2, 'Wrong C', FALSE), (8, 2, 'Wrong D', FALSE)"
        )

        # Challenge
        cur.execute(
            "INSERT INTO challenges (challenge_id, title, description, category, difficulty, xp_reward, is_active, created_by) "
            "VALUES (1, 'Test Challenge', 'desc', 'Waste Management', 'Easy', 20, TRUE, 2)"
        )

        # Badges matching the spec's rules
        cur.execute(
            "INSERT INTO badges (badge_id, name, description, icon, criteria_type, criteria_value, criteria_category) VALUES "
            "(1, 'Green Beginner', 'Complete first lesson', '🌱', 'lessons_completed', 1, NULL),"
            "(2, 'Eco Champion', 'Reach 1000 XP', '🏆', 'total_xp', 1000, NULL),"
            "(3, '7-Day Streak', 'Maintain 7-day streak', '🔥', 'streak_days', 7, NULL),"
            "(4, 'Recycling Hero', '5 waste-management challenges', '♻️', 'challenges_category', 2, 'Waste Management')"
        )


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def student_client(client):
    client.post("/login", data={"email": "student@test.com", "password": "password123"})
    return client


@pytest.fixture()
def teacher_client(client):
    client.post("/login", data={"email": "teacher@test.com", "password": "password123"})
    return client


@pytest.fixture()
def admin_client(client):
    client.post("/login", data={"email": "admin@test.com", "password": "password123"})
    return client
