"""Core gamification logic: XP, levels, badges and streaks.

Kept as plain functions operating on the database so the rules are easy to
read, unit-test and explain in a viva, rather than trusting any calculation
done in the browser.
"""
from datetime import date, timedelta
from flask import current_app
from utils.database import query_all, query_one, execute


def calculate_level(total_xp):
    """Level = floor(XP / 100) + 1."""
    xp_per_level = current_app.config["XP_PER_LEVEL"]
    return (total_xp // xp_per_level) + 1


def xp_for_next_level(total_xp):
    """XP still needed to reach the next level."""
    xp_per_level = current_app.config["XP_PER_LEVEL"]
    current_level = calculate_level(total_xp)
    next_level_threshold = current_level * xp_per_level
    return next_level_threshold - total_xp


def award_xp(user_id, amount, activity_type, description):
    """Add XP to a user, log the activity, and update their streak.

    Returns the badges (list of dicts) newly earned as a result of this
    award, so the caller can show a "badge unlocked" notification.
    """
    execute("UPDATE users SET total_xp = total_xp + %s WHERE user_id = %s", (amount, user_id))
    execute(
        "INSERT INTO activity_log (user_id, activity_type, description, xp_change, activity_date) "
        "VALUES (%s, %s, %s, %s, %s)",
        (user_id, activity_type, description, amount, date.today()),
    )
    update_streak(user_id)
    return check_and_award_badges(user_id)


def update_streak(user_id):
    """Increment the streak if the user was active yesterday or today.

    Rule (kept simple for viva explanability):
      - last_activity_date == today        -> streak unchanged (already counted today)
      - last_activity_date == yesterday     -> streak += 1
      - otherwise (gap of 2+ days, or first activity) -> streak resets to 1
    """
    user = query_one("SELECT current_streak, longest_streak, last_activity_date FROM users WHERE user_id = %s", (user_id,))
    if user is None:
        return

    today = date.today()
    last_date = user["last_activity_date"]

    if last_date == today:
        return  # already logged today, no change

    if last_date == today - timedelta(days=1):
        new_streak = user["current_streak"] + 1
    else:
        new_streak = 1

    new_longest = max(new_streak, user["longest_streak"])
    execute(
        "UPDATE users SET current_streak = %s, longest_streak = %s, last_activity_date = %s WHERE user_id = %s",
        (new_streak, new_longest, today, user_id),
    )

    if new_streak == 7:
        bonus = current_app.config["XP_STREAK_7_DAY_BONUS"]
        execute("UPDATE users SET total_xp = total_xp + %s WHERE user_id = %s", (bonus, user_id))
        execute(
            "INSERT INTO activity_log (user_id, activity_type, description, xp_change, activity_date) "
            "VALUES (%s, 'badge_earned', %s, %s, %s)",
            (user_id, "7-day streak bonus", bonus, today),
        )


def check_and_award_badges(user_id):
    """Check every badge's criteria against the user's current stats and
    award any not already earned. Returns the list of newly earned badges.
    """
    all_badges = query_all("SELECT * FROM badges")
    already_earned_ids = {
        row["badge_id"]
        for row in query_all("SELECT badge_id FROM user_badges WHERE user_id = %s", (user_id,))
    }
    user = query_one("SELECT total_xp, current_streak FROM users WHERE user_id = %s", (user_id,))

    newly_earned = []
    for badge in all_badges:
        if badge["badge_id"] in already_earned_ids:
            continue

        earned = False
        if badge["criteria_type"] == "lessons_completed":
            count = query_one(
                "SELECT COUNT(*) AS c FROM lesson_completions WHERE user_id = %s", (user_id,)
            )["c"]
            earned = count >= badge["criteria_value"]

        elif badge["criteria_type"] == "quizzes_completed":
            count = query_one(
                "SELECT COUNT(*) AS c FROM quiz_attempts WHERE user_id = %s", (user_id,)
            )["c"]
            earned = count >= badge["criteria_value"]

        elif badge["criteria_type"] == "challenges_category":
            count = query_one(
                "SELECT COUNT(*) AS c FROM challenge_completions cc "
                "JOIN challenges ch ON cc.challenge_id = ch.challenge_id "
                "WHERE cc.user_id = %s AND ch.category = %s",
                (user_id, badge["criteria_category"]),
            )["c"]
            earned = count >= badge["criteria_value"]

        elif badge["criteria_type"] == "streak_days":
            earned = user["current_streak"] >= badge["criteria_value"]

        elif badge["criteria_type"] == "total_xp":
            earned = user["total_xp"] >= badge["criteria_value"]

        if earned:
            execute(
                "INSERT IGNORE INTO user_badges (user_id, badge_id) VALUES (%s, %s)",
                (user_id, badge["badge_id"]),
            )
            execute(
                "INSERT INTO activity_log (user_id, activity_type, description, xp_change, activity_date) "
                "VALUES (%s, 'badge_earned', %s, 0, %s)",
                (user_id, f"Earned badge: {badge['name']}", date.today()),
            )
            newly_earned.append(badge)

    return newly_earned


def update_topic_progress(user_id, topic_id):
    """Recalculate a user's completion percentage for a topic."""
    total = query_one("SELECT COUNT(*) AS c FROM lessons WHERE topic_id = %s", (topic_id,))["c"]
    completed = query_one(
        "SELECT COUNT(*) AS c FROM lesson_completions lc "
        "JOIN lessons l ON lc.lesson_id = l.lesson_id "
        "WHERE lc.user_id = %s AND l.topic_id = %s",
        (user_id, topic_id),
    )["c"]
    percent = int((completed / total) * 100) if total > 0 else 0

    execute(
        "INSERT INTO user_progress (user_id, topic_id, lessons_completed, total_lessons, progress_percent) "
        "VALUES (%s, %s, %s, %s, %s) "
        "ON DUPLICATE KEY UPDATE lessons_completed = VALUES(lessons_completed), "
        "total_lessons = VALUES(total_lessons), progress_percent = VALUES(progress_percent)",
        (user_id, topic_id, completed, total, percent),
    )
    return percent
