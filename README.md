# EcoQuest 🌱

**Gamified Environmental Education Platform for Schools and Colleges**

> Learn. Play. Act. Make an Impact.

B.Tech Final Year Project — a web application that makes environmental
education interactive through lessons, quizzes, real-world challenges, XP,
levels, badges, streaks and leaderboards.

---

## Table of Contents

- [Problem Statement](#problem-statement)
- [Objectives](#objectives)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Database Setup](#database-setup)
- [Environment Variables](#environment-variables)
- [Running Locally](#running-locally)
- [Testing](#testing)
- [Demo Accounts](#demo-accounts)
- [Deployment](#deployment)
- [Limitations](#limitations)
- [Future Scope](#future-scope)
- [Documentation](#documentation)
- [Contributors](#contributors)

---

## Problem Statement

Environmental education is often taught in a traditional, theoretical way
that fails to engage students meaningfully, leaving awareness about
sustainability and eco-friendly practices limited. EcoQuest addresses this
by providing an interactive, gamified platform where students learn
environmental topics, take quizzes, complete real-world challenges, earn
XP, level up, unlock badges, maintain activity streaks and compete on a
leaderboard — while teachers get simple tools to author content and track
class performance, and admins manage the platform.

## Objectives

- Make environmental learning interactive and engaging rather than purely theoretical.
- Motivate consistent participation through gamification (XP, levels, badges, streaks).
- Give teachers a lightweight tool to author quizzes/challenges and monitor students.
- Provide administrators with content and user management.
- Keep the implementation understandable, correct and defendable for a B.Tech viva.

## Features

- **Authentication** — registration, login, logout, hashed passwords, role-based access (student/teacher/admin).
- **Learning module** — 6 environmental topics, 12 lessons with introduction/explanation/key points/eco-tip.
- **Quiz module** — multiple-choice quizzes, question-by-question navigation, scoring, XP, result review, attempt history.
- **Gamification** — XP system, level calculation, 6 automatically-unlocked badges, daily activity streaks.
- **Challenges** — real-world eco-friendly actions students mark complete for XP (once per day).
- **Leaderboard** — ranks students by total XP using SQL `RANK()`.
- **Progress analytics** — per-topic completion percentages with Chart.js visualizations.
- **Teacher dashboard** — class statistics, student performance, quiz/question/challenge authoring.
- **Admin dashboard** — platform-wide statistics, user/topic/lesson/quiz/challenge/badge management.
- **Responsive UI** — modern green, card-based design that works on desktop, tablet and mobile.

## Technology Stack

| Layer         | Technology                          |
|---------------|--------------------------------------|
| Frontend      | HTML5, CSS3, Vanilla JavaScript, Chart.js |
| Backend       | Python 3, Flask                     |
| Database      | MySQL 8                             |
| Auth          | Werkzeug password hashing, Flask sessions |
| Testing       | Pytest (44 tests against a real MySQL test database) |
| Version Control | Git, GitHub                       |
| Deployment    | Railway (or any WSGI-capable host)  |

**Why this stack?** Every technology above was already covered in the
B.Tech curriculum. Complex/trendy technologies (React, Node.js, MongoDB,
Docker, microservices, AI/ML, blockchain, etc.) were deliberately **not**
introduced — they would not improve the solution to this problem and would
make the implementation harder to defend in a viva. See
[`docs/architecture.md`](docs/architecture.md) for the full rationale.

## Architecture

Simple three-tier architecture:

```
User Browser
     |
HTML / CSS / JavaScript   (templates/, static/)
     |
Flask (routes, sessions, business logic)   (routes/, utils/)
     |
MySQL (data)   (database/)
```

Full details, including request flow and design decisions, are in
[`docs/architecture.md`](docs/architecture.md).

## Project Structure

```
ecoquest/
├── app.py                  # Flask app factory + entry point
├── config.py                # Config / TestConfig (env-driven)
├── requirements.txt
├── .env.example
├── .gitignore
│
├── database/
│   ├── schema.sql           # MySQL schema (14 tables)
│   └── seed.sql              # Demo data (topics, lessons, quizzes, etc.)
│
├── routes/
│   ├── auth.py               # register / login / logout
│   ├── student.py             # dashboard, topics, lessons, leaderboard, progress
│   ├── quiz.py                 # quiz taking, scoring, history, review
│   ├── challenge.py             # challenge listing + completion
│   ├── teacher.py                # teacher dashboard + authoring
│   └── admin.py                   # admin dashboard + management
│
├── utils/
│   ├── database.py           # PyMySQL connection helpers
│   ├── auth.py                 # password hashing, login/role decorators
│   └── gamification.py          # XP, levels, badges, streaks
│
├── templates/                 # Jinja2 templates (base, student/, teacher/, admin/)
├── static/                     # CSS, JS, images
│
├── tests/
│   ├── conftest.py            # pytest fixtures (real MySQL test DB)
│   ├── test_auth.py
│   ├── test_quiz.py
│   ├── test_gamification.py
│   └── test_database.py
│
└── docs/
    ├── architecture.md
    ├── database.md            # includes ER diagram (Mermaid)
    ├── dfd.md
    ├── srs.md
    ├── testing.md
    ├── uml.md
    ├── final_report.md
    └── presentation_outline.md
```

## Installation

Prerequisites: Python 3.10+, MySQL 8.x, pip.

```bash
git clone <repository-url>
cd ecoquest
python3 -m venv venv
source venv/bin/activate         # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Database Setup

```bash
mysql -u root -p < database/schema.sql
mysql -u root -p ecoquest < database/seed.sql
```

This creates the `ecoquest` database with 14 tables and loads demo data
(6 topics, 12 lessons, 6 quizzes, 30 questions/120 options, 12 challenges,
6 badges, and 3 demo accounts).

## Environment Variables

Copy `.env.example` to `.env` and fill in real values:

```bash
cp .env.example .env
```

| Variable      | Description                              |
|---------------|--------------------------------------------|
| `SECRET_KEY`  | Flask session signing key (long random string) |
| `DB_HOST`     | MySQL host                                  |
| `DB_PORT`     | MySQL port (default 3306)                   |
| `DB_USER`     | MySQL user                                  |
| `DB_PASSWORD` | MySQL password                              |
| `DB_NAME`     | Database name (`ecoquest`)                  |
| `TEST_DB_NAME`| Database used only by the automated test suite |

Never commit `.env` — it is already listed in `.gitignore`.

## Running Locally

```bash
python3 app.py
```

The app runs at `http://localhost:5000`.

## Testing

44 automated tests were written and **actually executed** against a real
MySQL test database (not mocked):

```bash
python3 -m pytest tests/ -v
```

Result at time of writing: **44 passed**. See
[`TEST_RESULTS.md`](TEST_RESULTS.md) and [`docs/testing.md`](docs/testing.md)
for the full test case documentation (25+ documented cases mapped to the
automated tests, plus the manually-verified end-to-end demo flow).

## Demo Accounts

| Role    | Email                     | Password     |
|---------|---------------------------|--------------|
| Student | student1@ecoquest.com     | student123   |
| Teacher | teacher1@ecoquest.com     | teacher123   |
| Admin   | admin1@ecoquest.com       | admin123     |

These are demo-only credentials seeded by `database/seed.sql`. Never reuse
them for a real deployment; create fresh accounts via the Admin panel or
registration form instead.

## Deployment

The app is deployment-ready for any platform that can run a Flask app
against a MySQL database (e.g. Railway):

1. Provision a MySQL database on the platform and run `schema.sql` (+ `seed.sql` if demo data is wanted).
2. Set the environment variables listed above (never hard-code secrets).
3. Set `PORT` if the platform requires a specific port (the app reads `PORT` from the environment).
4. Run the app with a production WSGI server, e.g. `gunicorn app:app`.

**Status:** prepared for deployment; not deployed to a live public URL as
part of this session (no cloud account/credentials were available to
provision one). See [`PROJECT_STATUS.md`](PROJECT_STATUS.md) for exact status.

## Limitations

- The Flask development server is used locally; a production WSGI server (e.g. gunicorn) should front it in production.
- Quiz option order is fixed (not shuffled) — acceptable for the current scope but a possible future enhancement.
- No email verification or password-reset flow.
- Streak/leaderboard rules are intentionally simple for viva explainability, not tuned for large-scale competitive gaming.

## Future Scope

- Certificate generation on course/topic completion.
- Dark mode.
- CSV/PDF export of class reports for teachers.
- Institution-level competitions.
- Installable PWA support.

(These are optional enhancements per the project brief and were **not**
implemented in this session — they are listed here only as future scope.)

## Documentation

| File | Contents |
|------|----------|
| [`docs/architecture.md`](docs/architecture.md) | System architecture, design rationale |
| [`docs/database.md`](docs/database.md) | Schema, relationships, ER diagram |
| [`docs/dfd.md`](docs/dfd.md) | Data Flow Diagrams (Level 0 & 1) |
| [`docs/srs.md`](docs/srs.md) | Software Requirements Specification |
| [`docs/uml.md`](docs/uml.md) | Class, sequence and activity diagrams |
| [`docs/testing.md`](docs/testing.md) | Test case documentation |
| [`docs/final_report.md`](docs/final_report.md) | B.Tech final report |
| [`docs/presentation_outline.md`](docs/presentation_outline.md) | Slide-by-slide presentation content |
| [`VIVA_QUESTIONS.md`](VIVA_QUESTIONS.md) | 100+ viva questions & answers |
| [`VIVA_CODING.md`](VIVA_CODING.md) | Coding-round questions with solutions |
| [`PROJECT_STATUS.md`](PROJECT_STATUS.md) | What's done, what's not, current status |
| [`TEST_RESULTS.md`](TEST_RESULTS.md) | Actual pytest execution output |
| [`TODO.md`](TODO.md) | Remaining/optional work |

## Contributors

Built as a B.Tech final year project by Anurag Patwari.
