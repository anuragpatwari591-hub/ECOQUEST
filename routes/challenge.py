"""Environmental challenge listing and completion."""
from datetime import date
from flask import Blueprint, render_template, session, redirect, url_for, flash, abort
from utils.database import query_all, query_one, execute
from utils.auth import role_required
from utils.gamification import award_xp

bp = Blueprint("challenge", __name__, url_prefix="/challenges")


@bp.route("/")
@role_required("student")
def list_challenges():
    user_id = session["user_id"]
    today = date.today()
    rows = query_all(
        "SELECT c.*, "
        "(cc.completion_id IS NOT NULL) AS completed_today "
        "FROM challenges c LEFT JOIN challenge_completions cc "
        "ON c.challenge_id = cc.challenge_id AND cc.user_id = %s AND cc.completed_on = %s "
        "WHERE c.is_active = TRUE ORDER BY c.challenge_id",
        (user_id, today),
    )
    return render_template("student/challenges.html", challenges=rows)


@bp.route("/<int:challenge_id>/complete", methods=["POST"])
@role_required("student")
def complete_challenge(challenge_id):
    user_id = session["user_id"]
    today = date.today()

    challenge = query_one(
        "SELECT * FROM challenges WHERE challenge_id = %s AND is_active = TRUE", (challenge_id,)
    )
    if challenge is None:
        abort(404)

    already_done = query_one(
        "SELECT completion_id FROM challenge_completions "
        "WHERE user_id = %s AND challenge_id = %s AND completed_on = %s",
        (user_id, challenge_id, today),
    )
    if already_done:
        flash("You already completed this challenge today.", "info")
        return redirect(url_for("challenge.list_challenges"))

    execute(
        "INSERT INTO challenge_completions (user_id, challenge_id, completed_on, xp_earned) "
        "VALUES (%s, %s, %s, %s)",
        (user_id, challenge_id, today, challenge["xp_reward"]),
    )
    new_badges = award_xp(
        user_id, challenge["xp_reward"], "challenge_completed",
        f"Completed challenge: {challenge['title']}",
    )

    flash(f"Challenge completed! +{challenge['xp_reward']} XP", "success")
    for badge in new_badges:
        flash(f"Badge unlocked: {badge['icon']} {badge['name']}!", "success")

    return redirect(url_for("challenge.list_challenges"))
