# Software Requirements Specification — EcoQuest

## 1. Introduction

### 1.1 Purpose
This document specifies the functional and non-functional requirements of
EcoQuest, a gamified environmental education web platform, developed as a
B.Tech final year project.

### 1.2 Scope
EcoQuest allows students to learn environmental topics, take quizzes,
complete real-world challenges and track gamified progress (XP, levels,
badges, streaks, leaderboard). Teachers can author quizzes/challenges and
view student performance. Admins manage users and content platform-wide.

### 1.3 Definitions
- **XP** — Experience Points, awarded for learning activities.
- **Badge** — An achievement automatically unlocked when a criterion is met.
- **Streak** — Number of consecutive days a student has been active.

### 1.4 Overall Description

**Product perspective:** a standalone three-tier web application (Flask +
MySQL), not part of a larger product family.

**Product functions:** see [Features](../README.md#features) in the README.

**User classes:**
| Class | Description |
|---|---|
| Student | Learns, plays quizzes, completes challenges, earns gamification rewards |
| Teacher | Authors quizzes/questions/challenges, views class analytics |
| Admin | Manages users and all educational content |

**Operating environment:** any modern browser (desktop/tablet/mobile);
server: Python 3.10+, MySQL 8, any OS that can run both.

**Design constraints:** must use only technologies covered in the B.Tech
curriculum (Flask, MySQL, HTML/CSS/JS) — see `docs/architecture.md` §2.

**Assumptions/dependencies:** a MySQL server is reachable from the Flask
process; users have a modern browser with JavaScript enabled (the app
degrades gracefully — core navigation/forms work without JS, but Chart.js
visualizations require it).

## 2. Functional Requirements

| ID | Requirement |
|---|---|
| FR-1 | The system shall allow a visitor to register as a student with name, email and password. |
| FR-2 | The system shall hash passwords before storage and never store plaintext. |
| FR-3 | The system shall authenticate users by email/password and start a session on success. |
| FR-4 | The system shall restrict pages by role (student/teacher/admin) and return HTTP 403 on violation. |
| FR-5 | The system shall display a student dashboard with real XP, level, streak, badge count and topic progress from the database. |
| FR-6 | The system shall let a student browse topics, view lessons and mark a lesson complete for XP. |
| FR-7 | The system shall let a student take a quiz question-by-question, score it server-side and award XP. |
| FR-8 | The system shall award a 50 XP bonus for a perfect quiz score. |
| FR-9 | The system shall let a student view past quiz attempts and review individual answers. |
| FR-10 | The system shall let a student mark a challenge complete once per calendar day and award XP. |
| FR-11 | The system shall reject a second completion of the same challenge on the same day. |
| FR-12 | The system shall calculate level as `floor(total_xp / 100) + 1`. |
| FR-13 | The system shall automatically award a badge when its criteria are met, without duplicate awards. |
| FR-14 | The system shall track a daily activity streak and award a bonus at 7 consecutive days. |
| FR-15 | The system shall rank students by total XP on a leaderboard using SQL. |
| FR-16 | The system shall let a teacher create a quiz and add questions with 4 options (one correct). |
| FR-17 | The system shall let a teacher create challenges. |
| FR-18 | The system shall show a teacher aggregated class statistics (avg score, active students, participation). |
| FR-19 | The system shall let an admin create/delete users and create topics, lessons, challenges. |
| FR-20 | The system shall show an admin platform-wide statistics (counts of users, content, attempts). |

## 3. Non-Functional Requirements

| ID | Requirement |
|---|---|
| NFR-1 | Passwords must be hashed with a strong algorithm (Werkzeug's `scrypt`). |
| NFR-2 | All SQL must use parameterized queries (no string-concatenated SQL). |
| NFR-3 | The UI must be responsive down to typical mobile widths (~360px). |
| NFR-4 | Secrets (DB password, Flask secret key) must be read from environment variables, never hard-coded. |
| NFR-5 | The application should respond to a typical dashboard request in well under 1 second on the seeded demo dataset (informal, not load-tested). |
| NFR-6 | Business-critical calculations (score, XP, level, badges) must be computed server-side, never trusted from client input. |

## 4. External Interface Requirements

- **UI:** server-rendered HTML via Jinja2, styled with a custom CSS design
  system (`static/css/style.css`), progressively enhanced with
  `static/js/main.js` and Chart.js (loaded from CDN) for charts.
- **Database interface:** PyMySQL connecting to MySQL 8 over TCP.

## 5. Security Requirements

- Passwords hashed, never logged or displayed.
- Session cookies signed with `SECRET_KEY`.
- Role checks enforced server-side on every protected route.
- All user input passed as SQL parameters, not interpolated into query strings.

## 6. Database Requirements

See [`docs/database.md`](database.md) for the full schema, ER diagram and
design rationale.

## 7. Acceptance Criteria

The system is considered acceptable when every item in the "Definition of
Done" checklist in [`PROJECT_STATUS.md`](../PROJECT_STATUS.md) is checked
and the automated test suite passes.

## 8. Future Scope

Certificate generation, dark mode, CSV/PDF export, institution-level
competitions, PWA support — listed as optional, **not implemented**.
