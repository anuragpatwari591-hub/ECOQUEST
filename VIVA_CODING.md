# EcoQuest — Coding Viva Questions

15 coding questions built directly from this project. Each includes the
question, a working solution consistent with the actual codebase, and a
short explanation. All code uses only Flask/PyMySQL/plain Python — nothing
outside the project's technology stack.

---

### 1. Write a basic Flask route.

```python
@bp.route("/hello")
def hello():
    return "Hello, EcoQuest!"
```
A route maps a URL to a Python function; Flask calls it when that URL is requested.

---

### 2. Connect Python to MySQL using PyMySQL.

```python
import pymysql
conn = pymysql.connect(
    host="localhost", user="ecoquest_user", password="...",
    database="ecoquest", cursorclass=pymysql.cursors.DictCursor,
)
```
This mirrors `utils/database.py::get_db()`, except that function stores
the connection on Flask's `g` object so it's reused for the whole request.

---

### 3. Insert a new user (with parameterized query).

```python
def create_user(cursor, name, email, password_hash, role="student"):
    cursor.execute(
        "INSERT INTO users (name, email, password_hash, role) VALUES (%s, %s, %s, %s)",
        (name, email, password_hash, role),
    )
```
`%s` placeholders + a tuple of values prevent SQL injection — never format
user input directly into the SQL string.

---

### 4. Retrieve a user by email.

```python
def get_user_by_email(cursor, email):
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    return cursor.fetchone()
```

---

### 5. Write a SELECT with a JOIN (lessons + their topic name).

```sql
SELECT l.title, t.name AS topic_name
FROM lessons l
JOIN topics t ON l.topic_id = t.topic_id
WHERE l.topic_id = %s;
```

---

### 6. Calculate a quiz score given a list of (question_id, selected_option_id) and the DB.

```python
def calculate_score(cursor, answers):
    """answers: list of (question_id, selected_option_id)."""
    correct = 0
    for question_id, option_id in answers:
        cursor.execute(
            "SELECT is_correct FROM options WHERE option_id = %s AND question_id = %s",
            (option_id, question_id),
        )
        row = cursor.fetchone()
        if row and row["is_correct"]:
            correct += 1
    return correct, len(answers)
```
This is exactly the logic in `routes/quiz.py::submit_quiz()`: never trust a
score submitted by the client — recompute it from the database.

---

### 7. Calculate XP earned for a quiz attempt (10 XP/correct answer + 50 bonus for a perfect score).

```python
def calculate_quiz_xp(correct, total):
    xp = correct * 10
    if correct == total:
        xp += 50
    return xp
```

---

### 8. Calculate a student's level from total XP.

```python
def calculate_level(total_xp, xp_per_level=100):
    return (total_xp // xp_per_level) + 1
```
Integer division (`//`) implements `floor()`. Example: `calculate_level(1240)` → `13`.

---

### 9. Check whether a student is eligible for the "Eco Champion" badge (>= 1000 XP).

```python
def is_eligible_for_eco_champion(cursor, user_id):
    cursor.execute("SELECT total_xp FROM users WHERE user_id = %s", (user_id,))
    user = cursor.fetchone()
    return user is not None and user["total_xp"] >= 1000
```

---

### 10. Calculate the leaderboard (top 10 students by XP).

```sql
SELECT name, total_xp, RANK() OVER (ORDER BY total_xp DESC) AS rnk
FROM users
WHERE role = 'student'
ORDER BY total_xp DESC
LIMIT 10;
```

---

### 11. Implement login validation (password check, no plaintext comparison).

```python
from werkzeug.security import check_password_hash

def validate_login(cursor, email, password):
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    if user is None:
        return None
    if not check_password_hash(user["password_hash"], password):
        return None
    return user
```

---

### 12. Implement a role-based authorization check as a Flask decorator.

```python
from functools import wraps
from flask import session, abort

def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(*args, **kwargs):
            if "user_id" not in session:
                abort(401)
            if session.get("role") not in roles:
                abort(403)
            return view_func(*args, **kwargs)
        return wrapped
    return decorator

@bp.route("/admin/dashboard")
@role_required("admin")
def admin_dashboard():
    ...
```

---

### 13. Calculate a student's completion percentage for one topic.

```python
def topic_progress_percent(cursor, user_id, topic_id):
    cursor.execute("SELECT COUNT(*) AS c FROM lessons WHERE topic_id = %s", (topic_id,))
    total = cursor.fetchone()["c"]
    if total == 0:
        return 0
    cursor.execute(
        "SELECT COUNT(*) AS c FROM lesson_completions lc "
        "JOIN lessons l ON lc.lesson_id = l.lesson_id "
        "WHERE lc.user_id = %s AND l.topic_id = %s",
        (user_id, topic_id),
    )
    completed = cursor.fetchone()["c"]
    return int((completed / total) * 100)
```

---

### 14. Prevent a student from completing the same challenge twice on the same day.

```python
from datetime import date

def complete_challenge_once_per_day(cursor, user_id, challenge_id, xp_reward):
    today = date.today()
    cursor.execute(
        "SELECT completion_id FROM challenge_completions "
        "WHERE user_id = %s AND challenge_id = %s AND completed_on = %s",
        (user_id, challenge_id, today),
    )
    if cursor.fetchone():
        return False  # already completed today
    cursor.execute(
        "INSERT INTO challenge_completions (user_id, challenge_id, completed_on, xp_earned) "
        "VALUES (%s, %s, %s, %s)",
        (user_id, challenge_id, today, xp_reward),
    )
    return True
```
The database also enforces this independently via a
`UNIQUE (user_id, challenge_id, completed_on)` constraint, so even a race
condition between two simultaneous requests can't create a duplicate row.

---

### 15. Update a student's daily activity streak.

```python
from datetime import date, timedelta

def update_streak(cursor, user_id):
    cursor.execute(
        "SELECT current_streak, longest_streak, last_activity_date FROM users WHERE user_id = %s",
        (user_id,),
    )
    user = cursor.fetchone()
    today = date.today()

    if user["last_activity_date"] == today:
        return  # already counted today

    if user["last_activity_date"] == today - timedelta(days=1):
        new_streak = user["current_streak"] + 1
    else:
        new_streak = 1

    new_longest = max(new_streak, user["longest_streak"])
    cursor.execute(
        "UPDATE users SET current_streak = %s, longest_streak = %s, last_activity_date = %s "
        "WHERE user_id = %s",
        (new_streak, new_longest, today, user_id),
    )
```
This is the real logic in `utils/gamification.py::update_streak()`,
included here verbatim in spirit because it's a favorite viva question:
"explain your streak algorithm and write it from scratch."
