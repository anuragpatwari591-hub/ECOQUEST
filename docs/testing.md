# EcoQuest — Testing Documentation

## 1. Testing Approach

All automated tests run with **pytest** against a **real MySQL database**
(`ecoquest_test`), not mocks — `tests/conftest.py` drops and rebuilds the
schema from `database/schema.sql` before every test function and seeds a
small deterministic fixture. This means the actual SQL in
`utils/database.py`, `utils/gamification.py` and the route modules is
exercised exactly as it runs in production.

Automated tests were supplemented by a manual end-to-end script
(`demo_flow.py`, run against the live dev server with the full seed
dataset) that walks the complete student → teacher → admin journey from
the project brief over real HTTP requests.

**Actual result at time of writing:** `44 passed` (see
[`TEST_RESULTS.md`](../TEST_RESULTS.md) for the raw pytest output).

## 2. Test Case Documentation

| ID | Description | Precondition | Steps | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|---|
| TC-01 | Register with valid data | None | POST /register with valid name/email/password | Account created, redirected to login | Account created | PASS |
| TC-02 | Register with duplicate email | An account with that email exists | POST /register with same email | "already exists" error shown | Error shown | PASS |
| TC-03 | Register with mismatched passwords | None | POST /register, password != confirm_password | "do not match" error shown | Error shown | PASS |
| TC-04 | Password stored hashed | User registered | Query `users.password_hash` | Value is a scrypt hash, not plaintext | Confirmed `scrypt:...` | PASS |
| TC-05 | Login with valid credentials | Registered user exists | POST /login with correct email/password | Session created, "Welcome back" shown | Session created | PASS |
| TC-06 | Login with wrong password | Registered user exists | POST /login with wrong password | "Invalid email or password" | Error shown | PASS |
| TC-07 | Login with non-existent email | None | POST /login with unknown email | "Invalid email or password" | Error shown | PASS |
| TC-08 | Logout clears session | Logged in | GET /logout, then GET /student/dashboard | Redirected to login (302) | Redirected | PASS |
| TC-09 | Student blocked from admin pages | Logged in as student | GET /admin/dashboard | HTTP 403 | 403 returned | PASS |
| TC-10 | Student blocked from teacher pages | Logged in as student | GET /teacher/dashboard | HTTP 403 | 403 returned | PASS |
| TC-11 | Teacher blocked from admin pages | Logged in as teacher | GET /admin/dashboard | HTTP 403 | 403 returned | PASS |
| TC-12 | Admin can access admin dashboard | Logged in as admin | GET /admin/dashboard | HTTP 200 | 200 returned | PASS |
| TC-13 | Admin blocked from student dashboard | Logged in as admin | GET /student/dashboard | HTTP 403 | 403 returned | PASS |
| TC-14 | Unauthenticated access redirected | Not logged in | GET /student/dashboard | Redirect to /login (302) | Redirected | PASS |
| TC-15 | Perfect quiz score calculation | Quiz with 2 questions | Answer both correctly | Score 2/2 shown, perfect bonus shown | "2/2" + bonus shown | PASS |
| TC-16 | Partial-correct quiz score | Quiz with 2 questions | Answer 1 correct, 1 wrong | Score 1/2, no perfect bonus | "1/2", no bonus | PASS |
| TC-17 | XP calculation for correct answers | 1 correct answer | Submit quiz | `xp_earned` = 10 in `quiz_attempts` | xp_earned = 10 | PASS |
| TC-18 | Perfect-score XP bonus | 2/2 correct | Submit quiz | `xp_earned` = 2×10 + 50 = 70 | xp_earned = 70 | PASS |
| TC-19 | Quiz attempt + answers persisted | Quiz submitted | Query `quiz_attempts`, `quiz_answers` | 1 attempt row, 2 answer rows | Confirmed | PASS |
| TC-20 | Student total_xp increases after quiz | Quiz submitted | Compare `users.total_xp` before/after | Increases by xp_earned | +70 confirmed | PASS |
| TC-21 | Level = floor(XP/100)+1 (boundary 0) | XP = 0 or 99 | Call `calculate_level` | Level 1 | Level 1 | PASS |
| TC-22 | Level boundary at 100 | XP = 100 or 199 | Call `calculate_level` | Level 2 | Level 2 | PASS |
| TC-23 | Level for higher XP | XP = 1240 | Call `calculate_level` | Level 13 | Level 13 | PASS |
| TC-24 | XP needed for next level | XP = 50 / 120 | Call `xp_for_next_level` | 50 / 80 respectively | 50 / 80 | PASS |
| TC-25 | award_xp increases total_xp | Fixture user at 90 XP | `award_xp(user, 25, ...)` | total_xp = 115 | 115 | PASS |
| TC-26 | award_xp logs activity | Any award | `award_xp(...)` | Row in `activity_log` with matching description/xp | Confirmed | PASS |
| TC-27 | Badge unlocked on first lesson | No lessons completed | Complete 1 lesson | "Green Beginner" badge flashed + row in `user_badges` | Confirmed | PASS |
| TC-28 | Badge unlocked on XP threshold | XP just under 1000 | Award XP crossing 1000 | "Eco Champion" in returned new badges | Confirmed | PASS |
| TC-29 | Badge not awarded twice | Badge already earned | Re-check badge criteria | Second check returns no duplicate | Confirmed | PASS |
| TC-30 | Streak increments on consecutive day | last_activity = yesterday | Trigger any XP award today | current_streak += 1 | +1 confirmed | PASS |
| TC-31 | Streak resets after a gap | last_activity = 3 days ago | Trigger any XP award today | current_streak = 1 | Reset to 1 | PASS |
| TC-32 | 7-day streak bonus badge | streak about to hit 7 | Trigger XP award | "7-Day Streak" badge + 100 bonus XP | Confirmed | PASS |
| TC-33 | Challenge completion awards XP | Challenge not done today | POST complete | total_xp increases by challenge's xp_reward | +20 confirmed | PASS |
| TC-34 | Duplicate challenge completion blocked | Challenge already done today | POST complete again | "already completed" message, XP unchanged | Confirmed | PASS |
| TC-35 | Category-based badge (e.g. Recycling Hero) | 2 waste-mgmt challenges done | Check badges | Badge awarded | Confirmed | PASS |
| TC-36 | Row insertion + retrieval | DB available | INSERT topic, SELECT it back | Row matches inserted values | Confirmed | PASS |
| TC-37 | Row update | Existing user | UPDATE name, SELECT | New name reflected | Confirmed | PASS |
| TC-38 | Row deletion | Existing row | DELETE, SELECT | Row is gone (None) | Confirmed | PASS |
| TC-39 | FK cascade delete | Topic with a lesson | DELETE topic | Lesson also deleted (CASCADE) | Confirmed | PASS |
| TC-40 | Unique constraint on email | Existing user | INSERT duplicate email | `IntegrityError` raised | Raised | PASS |
| TC-41 | Unique constraint on lesson completion | Lesson completed once | INSERT duplicate completion | `IntegrityError` raised | Raised | PASS |
| TC-42 | Quiz → Questions 1:N | Fixture quiz | SELECT questions WHERE quiz_id | 2 rows returned | 2 rows | PASS |
| TC-43 | Question → Options 1:N | Fixture question | SELECT options WHERE question_id | 4 rows, 1 correct | 4 rows, 1 correct | PASS |
| TC-44 | Leaderboard SQL ordering | Multiple students, varying XP | `ORDER BY total_xp DESC` | Highest XP student first | Confirmed | PASS |
| TC-45 (manual) | Full demo flow: register → login → lesson → quiz → challenge → leaderboard → logout → teacher → admin | Live server + seeded DB | Run `demo_flow.py` end to end | All 29 checks pass, no server errors | All checks passed, server log clean | PASS |

Test cases TC-01 through TC-44 map 1:1 to the 44 automated pytest tests in
`tests/`. TC-45 is the manual end-to-end verification described in
`PROJECT_STATUS.md`.

## 3. What Was NOT Tested

- **Load/performance testing** — not performed; the app has not been
  benchmarked under concurrent load. Marked as **not evaluated**.
- **Cross-browser testing** — only verified via HTTP-level requests and
  manual review of rendered HTML/CSS; no automated browser (Selenium/
  Playwright) testing was set up. Marked as **not evaluated**.
- **Actual cloud deployment** — the app was verified to run locally
  against real MySQL; it was not deployed to a live public URL in this
  session (see `PROJECT_STATUS.md`). Marked as **not evaluated**.

No test result in this document or in `TEST_RESULTS.md` was fabricated;
every PASS reflects an actual pytest run or an actual manual HTTP session
against the running application.
