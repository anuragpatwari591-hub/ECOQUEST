"""Tests for XP, level calculation, badge unlocking and streaks."""
from datetime import date, timedelta
from utils.gamification import calculate_level, xp_for_next_level, award_xp, check_and_award_badges
from utils.database import query_one, execute


def test_level_calculation_level_1(app):
    with app.app_context():
        assert calculate_level(0) == 1
        assert calculate_level(99) == 1


def test_level_calculation_level_2(app):
    with app.app_context():
        assert calculate_level(100) == 2
        assert calculate_level(199) == 2


def test_level_calculation_higher_levels(app):
    with app.app_context():
        assert calculate_level(1240) == 13
        assert calculate_level(1000) == 11


def test_xp_for_next_level(app):
    with app.app_context():
        assert xp_for_next_level(50) == 50
        assert xp_for_next_level(120) == 80


def test_award_xp_increases_total_xp(app):
    with app.app_context():
        award_xp(1, 25, "lesson_completed", "test activity")
        user = query_one("SELECT total_xp FROM users WHERE user_id = 1")
    assert user["total_xp"] == 115  # fixture starts at 90


def test_award_xp_logs_activity(app):
    with app.app_context():
        award_xp(1, 10, "lesson_completed", "Completed Test Lesson")
        log = query_one(
            "SELECT * FROM activity_log WHERE user_id = 1 ORDER BY log_id DESC LIMIT 1"
        )
    assert log["description"] == "Completed Test Lesson"
    assert log["xp_change"] == 10


def test_badge_unlocked_on_first_lesson_completion(app, student_client):
    student_client.get("/student/lessons/1")
    response = student_client.post("/student/lessons/1/complete", follow_redirects=True)
    assert b"Green Beginner" in response.data
    with app.app_context():
        earned = query_one(
            "SELECT * FROM user_badges WHERE user_id = 1 AND badge_id = 1"
        )
    assert earned is not None


def test_badge_unlocked_on_reaching_xp_threshold(app):
    with app.app_context():
        execute("UPDATE users SET total_xp = 990 WHERE user_id = 1")
        new_badges = award_xp(1, 20, "quiz_attempted", "boost over 1000 xp")
    names = [b["name"] for b in new_badges]
    assert "Eco Champion" in names


def test_badge_not_awarded_twice(app):
    with app.app_context():
        execute("UPDATE users SET total_xp = 1500 WHERE user_id = 1")
        first = check_and_award_badges(1)
        second = check_and_award_badges(1)
    assert any(b["name"] == "Eco Champion" for b in first)
    assert not any(b["name"] == "Eco Champion" for b in second)


def test_streak_increments_on_consecutive_day(app):
    with app.app_context():
        yesterday = date.today() - timedelta(days=1)
        execute(
            "UPDATE users SET current_streak = 3, longest_streak = 3, last_activity_date = %s WHERE user_id = 1",
            (yesterday,),
        )
        award_xp(1, 10, "lesson_completed", "day activity")
        user = query_one("SELECT current_streak FROM users WHERE user_id = 1")
    assert user["current_streak"] == 4


def test_streak_resets_after_gap(app):
    with app.app_context():
        three_days_ago = date.today() - timedelta(days=3)
        execute(
            "UPDATE users SET current_streak = 5, longest_streak = 5, last_activity_date = %s WHERE user_id = 1",
            (three_days_ago,),
        )
        award_xp(1, 10, "lesson_completed", "activity after gap")
        user = query_one("SELECT current_streak FROM users WHERE user_id = 1")
    assert user["current_streak"] == 1


def test_seven_day_streak_badge(app):
    with app.app_context():
        yesterday = date.today() - timedelta(days=1)
        execute(
            "UPDATE users SET current_streak = 6, longest_streak = 6, last_activity_date = %s WHERE user_id = 1",
            (yesterday,),
        )
        new_badges = award_xp(1, 10, "lesson_completed", "7th day")
    names = [b["name"] for b in new_badges]
    assert "7-Day Streak" in names


def test_challenge_completion_awards_xp(app, student_client):
    with app.app_context():
        xp_before = query_one("SELECT total_xp FROM users WHERE user_id = 1")["total_xp"]
    response = student_client.post("/challenges/1/complete", follow_redirects=True)
    assert response.status_code == 200
    with app.app_context():
        xp_after = query_one("SELECT total_xp FROM users WHERE user_id = 1")["total_xp"]
    assert xp_after == xp_before + 20


def test_duplicate_challenge_completion_same_day_blocked(app, student_client):
    student_client.post("/challenges/1/complete", follow_redirects=True)
    with app.app_context():
        xp_after_first = query_one("SELECT total_xp FROM users WHERE user_id = 1")["total_xp"]

    response = student_client.post("/challenges/1/complete", follow_redirects=True)
    assert b"already completed" in response.data.lower()

    with app.app_context():
        xp_after_second = query_one("SELECT total_xp FROM users WHERE user_id = 1")["total_xp"]
    assert xp_after_first == xp_after_second


def test_challenges_category_badge(app):
    with app.app_context():
        execute(
            "INSERT INTO challenge_completions (user_id, challenge_id, completed_on, xp_earned) VALUES "
            "(1, 1, CURDATE(), 20)"
        )
        execute(
            "INSERT INTO challenge_completions (user_id, challenge_id, completed_on, xp_earned) VALUES "
            "(1, 1, %s, 20)",
            (date.today() - timedelta(days=1),),
        )
        new_badges = check_and_award_badges(1)
    names = [b["name"] for b in new_badges]
    assert "Recycling Hero" in names
