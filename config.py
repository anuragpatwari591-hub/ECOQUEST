"""Application configuration loaded from environment variables."""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

    DB_HOST = os.environ.get("DB_HOST", "localhost")
    DB_PORT = int(os.environ.get("DB_PORT", 3306))
    DB_USER = os.environ.get("DB_USER", "ecoquest_user")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
    DB_NAME = os.environ.get("DB_NAME", "ecoquest")

    # XP rewards (kept centralized so gamification rules are easy to tune/explain)
    XP_LESSON_COMPLETE = 10
    XP_CORRECT_ANSWER = 10
    XP_PERFECT_QUIZ_BONUS = 50
    XP_STREAK_7_DAY_BONUS = 100

    XP_PER_LEVEL = 100


class TestConfig(Config):
    TESTING = True
    DB_NAME = os.environ.get("TEST_DB_NAME", "ecoquest_test")
