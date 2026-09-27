# EcoQuest — Final Project Report

**A Gamified Environmental Education Platform for Schools and Colleges**
B.Tech Final Year Project

_Note on scope: this is a condensed report covering all 15 standard
chapters. Every claim below reflects work actually done in this project —
where something was not implemented, tested or deployed, it is labeled
"planned" or "not evaluated" rather than presented as complete._

---

## Chapter 1 — Introduction

Environmental awareness is critical, yet traditional classroom instruction
on sustainability topics is often theoretical and fails to hold student
interest. EcoQuest is a web-based platform that reframes environmental
education as an interactive, gamified experience — students learn topics,
take quizzes, complete real-world eco-challenges, and are rewarded with
XP, levels, badges and leaderboard standing.

## Chapter 2 — Problem Definition

Students frequently disengage from environmental education because it is
delivered passively (lectures, textbooks) with no feedback loop or
incentive for participation. There is a need for a platform that makes
learning measurable, interactive and rewarding, for both students (a
motivating experience) and teachers (a tool to track engagement).

## Chapter 3 — Existing System

Most schools rely on textbook-based environmental science instruction with
occasional posters, competitions or one-off awareness events. These are
not digitally tracked, not personalized, and provide no continuous
feedback or incentive structure for students.

## Chapter 4 — Proposed System

EcoQuest proposes a three-role web platform (Student/Teacher/Admin) built
on Flask and MySQL that:
- Delivers structured lessons and quizzes per environmental topic.
- Converts real-world eco-friendly actions into trackable "challenges."
- Rewards all of the above through a unified XP/level/badge/streak system.
- Gives teachers and admins dashboards to author content and monitor usage.

## Chapter 5 — Requirement Analysis

See [`docs/srs.md`](srs.md) for the full functional (FR-1..FR-20) and
non-functional (NFR-1..NFR-6) requirements, derived directly from the
project brief and validated against the implemented features.

## Chapter 6 — Feasibility Study

- **Technical feasibility:** Flask, MySQL and vanilla JS are open-source,
  well-documented, and already known from the curriculum — confirmed
  feasible by the fact that the full application was built and runs.
- **Operational feasibility:** the demo flow (register → learn → quiz →
  challenge → leaderboard → teacher/admin views) was manually verified
  end-to-end, confirming the intended user journey works.
- **Economic feasibility:** no paid services are required to run the app
  locally; cloud hosting (if pursued) has free/low-cost tiers on platforms
  like Railway.

## Chapter 7 — System Design

Three-tier architecture (Presentation → Application → Data). Full
rationale, diagrams and request-flow walkthroughs are in
[`docs/architecture.md`](architecture.md), [`docs/dfd.md`](dfd.md) and
[`docs/uml.md`](uml.md).

## Chapter 8 — Database Design

14 relational tables covering users, content and activity, fully
normalized with foreign keys, unique constraints and indexes. Full schema
and ER diagram: [`docs/database.md`](database.md).

## Chapter 9 — Implementation

Implemented in Python/Flask across six blueprints (`auth`, `student`,
`quiz`, `challenge`, `teacher`, `admin`), with shared logic centralized in
`utils/` (`database.py`, `auth.py`, `gamification.py`). The frontend uses
server-rendered Jinja2 templates styled with a custom CSS design system,
progressively enhanced with vanilla JavaScript and Chart.js. Demo data
(6 topics, 12 lessons, 6 quizzes, 30 questions, 12 challenges, 6 badges)
was seeded via `database/seed.sql`.

## Chapter 10 — Testing

44 automated pytest tests were written and **actually executed** against a
real MySQL test database, covering authentication, authorization (all
three roles), quiz scoring/XP, gamification (levels/badges/streaks) and
database integrity. Result: **44/44 passed.** A manual 29-step end-to-end
script was also run against the live application and passed completely.
Full details: [`docs/testing.md`](testing.md), [`TEST_RESULTS.md`](../TEST_RESULTS.md).

**Not performed:** load/performance testing, automated cross-browser UI
testing (Selenium/Playwright). These are explicitly marked as
**not evaluated**, not assumed to pass.

## Chapter 11 — Results

- All core features function correctly end-to-end: registration, login,
  role authorization, learning module, quiz module with correct scoring
  and XP, gamification (levels/badges/streaks), challenges with
  duplicate-prevention, leaderboard, and both teacher and admin dashboards.
- The demo dataset (seeded via `seed.sql`) exercises every table and
  relationship in the schema.
- No errors were observed in the Flask server log during either the
  automated test run or the manual end-to-end session.

## Chapter 12 — Deployment

The application is deployment-ready: all configuration is environment-
variable driven, no secrets are hard-coded, and `PORT` is read from the
environment for cloud compatibility. **Status: prepared but not deployed**
to a live public URL in this session, as no cloud hosting account/
credentials were available. Deployment steps are documented in the
README's "Deployment" section.

## Chapter 13 — Limitations

- Not yet deployed to a live public URL.
- Quiz option order is fixed rather than randomized per attempt.
- Multi-row writes during quiz submission are not wrapped in an explicit
  database transaction (each statement runs with `autocommit=True`).
- No automated browser/UI or load testing was performed.
- No password-reset or email-verification flow.

## Chapter 14 — Future Scope

Certificate generation, dark mode, CSV/PDF export for teachers,
institution-level competitions, and installable PWA support are identified
as reasonable next steps, explicitly deferred as optional per the project
brief's own prioritization (core functionality first).

## Chapter 15 — Conclusion

EcoQuest demonstrates that a deliberately simple, curriculum-appropriate
technology stack (Flask + MySQL + vanilla JS) can deliver a complete,
gamified educational platform without overengineering. Every feature in
the original problem statement — learning, quizzes, challenges, XP,
levels, badges, streaks, leaderboards, and role-specific dashboards — is
implemented, working, and verified by 44 automated tests plus a full
manual demo walkthrough.

## References

- Flask documentation — https://flask.palletsprojects.com/
- MySQL 8 Reference Manual — https://dev.mysql.com/doc/refman/8.0/en/
- PyMySQL documentation — https://pymysql.readthedocs.io/
- Werkzeug security documentation — https://werkzeug.palletsprojects.com/en/stable/utils/#module-werkzeug.security

## Appendix

- Full schema: [`database/schema.sql`](../database/schema.sql)
- Demo data: [`database/seed.sql`](../database/seed.sql)
- Test results: [`TEST_RESULTS.md`](../TEST_RESULTS.md)
- Viva preparation: [`VIVA_QUESTIONS.md`](../VIVA_QUESTIONS.md), [`VIVA_CODING.md`](../VIVA_CODING.md)
