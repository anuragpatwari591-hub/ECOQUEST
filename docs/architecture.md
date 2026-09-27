# EcoQuest — System Architecture

## 1. Architectural Style: Three-Tier

EcoQuest uses a classic three-tier web architecture, chosen deliberately
for its simplicity and because every layer maps directly to technology
covered in the B.Tech curriculum.

```
┌─────────────────────────────────────────────┐
│  Presentation Layer                          │
│  HTML5 + CSS3 + Vanilla JavaScript (Jinja2   │
│  templates rendered server-side)             │
└───────────────────┬───────────────────────────┘
                    │ HTTP request/response
┌───────────────────▼───────────────────────────┐
│  Application Layer                           │
│  Python + Flask                              │
│    - routes/   (HTTP endpoints, one blueprint │
│                 per role/module)              │
│    - utils/    (auth, gamification, DB access)│
└───────────────────┬───────────────────────────┘
                    │ SQL (PyMySQL)
┌───────────────────▼───────────────────────────┐
│  Data Layer                                  │
│  MySQL 8 — 14 relational tables               │
└─────────────────────────────────────────────┘
```

## 2. Why This Stack (and not something else)

| Technology considered | Decision | Reason |
|---|---|---|
| Flask vs Django | **Flask** | Lighter, every line of routing/config is visible and explainable; Django's implicit ORM/ admin magic is harder to defend line-by-line in a viva. |
| MySQL vs MongoDB/Firebase | **MySQL** | The data (users, quizzes, attempts, badges) is inherently relational with clear foreign keys — a relational DB is the textbook-correct choice, and SQL joins/normalization are a required B.Tech topic. |
| Vanilla JS vs React/Vue | **Vanilla JS** | Server-rendered Jinja2 templates + a few DOM helpers are sufficient for this app's interactivity (nav toggle, flash auto-dismiss, quiz option highlight). React would add a build pipeline and a second "language" (JSX) without solving any problem this app actually has. |
| Session-based auth vs JWT/OAuth | **Flask sessions** | The app has one first-party frontend, not a public API consumed by third parties — sessions are simpler, are covered in the curriculum, and avoid the extra complexity of token refresh/revocation. |
| No Docker/Kubernetes | Plain WSGI deployment | A single Flask app + one MySQL database does not need container orchestration; it adds operational complexity with no corresponding benefit at this scale. |

## 3. Request Flow (example: completing a lesson)

```
Browser: POST /student/lessons/4/complete
   │
   ▼
routes/student.py: complete_lesson()
   │  - @role_required("student") checks session
   │  - SELECT lesson by id (utils/database.query_one)
   │  - Check lesson_completions for existing row (idempotency)
   │  - INSERT into lesson_completions
   │  - utils/gamification.update_topic_progress()  -> recompute % for that topic
   │  - utils/gamification.award_xp()
   │       - UPDATE users SET total_xp += reward
   │       - INSERT INTO activity_log
   │       - update_streak()
   │       - check_and_award_badges()
   │  - flash() messages queued
   ▼
redirect -> GET /student/topics/<topic_id>
   │
   ▼
Jinja2 template renders updated state (fresh SELECTs)
```

All business rules (score, XP, level, badge, streak) are computed **in
Flask/Python against the database**, never trusted from the browser —
this is a deliberate security/correctness decision, not an oversight.

## 4. Blueprints (modularity)

The Flask app is split into six blueprints, each owning one concern:

- `auth` — registration/login/logout (no role required)
- `student` — dashboard, topics, lessons, leaderboard, progress, profile
- `quiz` — quiz taking, scoring, history, review
- `challenge` — challenge listing + completion
- `teacher` — teacher dashboard, student view, quiz authoring, challenge authoring
- `admin` — admin dashboard, user/topic/lesson/quiz/challenge/badge management

Each blueprint's routes are protected with the `@role_required(...)`
decorator from `utils/auth.py`, which checks the Flask session before the
view function runs.

## 5. Deployment Architecture

```
GitHub (source of truth)
   │
   ▼
Cloud host (e.g. Railway) running:
   - Flask app via a WSGI server (gunicorn)
   - Environment variables for SECRET_KEY / DB credentials
   │
   ▼
Managed MySQL database (schema.sql applied once at provisioning)
```

No API gateway, message queue, or microservice split is used — one Flask
process talks directly to one MySQL database, which is sufficient for the
project's scale and keeps the deployment diagram simple enough to draw and
explain from memory.
