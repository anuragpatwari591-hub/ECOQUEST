# EcoQuest — Presentation Outline (18 Slides)

Content for each slide is provided below; use it to build the actual
slide deck (e.g. PowerPoint/Google Slides). No slide claims a result that
wasn't actually produced in this project.

---

**Slide 1 — Title**
EcoQuest — Gamified Environmental Education Platform
"Learn. Play. Act. Make an Impact."
B.Tech Final Year Project | [Your Name] | [Institution]

**Slide 2 — Problem Statement**
Traditional environmental education is theoretical and disengaging;
awareness of sustainability practices remains limited among students.

**Slide 3 — Motivation**
Gamification (XP, levels, badges) is a proven way to sustain engagement.
Applying it to environmental learning turns passive content into an
active, rewarding habit.

**Slide 4 — Objectives**
- Make environmental learning interactive
- Reward consistent participation via gamification
- Give teachers tools to author content and track engagement
- Give admins platform-wide management

**Slide 5 — Existing System**
Textbook-based instruction, occasional posters/competitions — not
digitally tracked, not personalized, no feedback loop.

**Slide 6 — Proposed System**
A three-role (Student/Teacher/Admin) Flask + MySQL web app: lessons,
quizzes, real-world challenges, and a full gamification layer.

**Slide 7 — Features**
Learning module · Quiz module · Challenges · XP & Levels · Badges ·
Streaks · Leaderboard · Progress analytics · Teacher & Admin dashboards

**Slide 8 — System Architecture**
Three-tier: Browser (HTML/CSS/JS) → Flask (routes + business logic) →
MySQL. (Diagram from `docs/architecture.md`.)

**Slide 9 — Technology Stack**
Python/Flask · MySQL · HTML5/CSS3/JS · Chart.js · Pytest · Git/GitHub.
Chosen for curriculum alignment and viva-defensibility — not
overengineered with React/Node/Docker/AI.

**Slide 10 — Data Flow Diagram**
Level 0 context diagram + Level 1 process breakdown. (From `docs/dfd.md`.)

**Slide 11 — ER Diagram**
14-table relational schema — users, topics, lessons, quizzes, questions,
options, attempts, challenges, badges, progress, activity log.
(From `docs/database.md`.)

**Slide 12 — Gamification Design**
XP rules (lesson +10, correct answer +10, perfect quiz +50, 7-day streak
+100) · Level = floor(XP/100)+1 · 6 auto-unlocked badges · daily streak
logic.

**Slide 13 — Student Dashboard (Screenshot)**
[Insert screenshot of the running dashboard: XP, level, streak, badges,
topic progress bars, today's challenge, recent activity.]

**Slide 14 — Teacher / Admin Dashboards (Screenshot)**
[Insert screenshots: teacher class analytics + charts; admin platform
statistics.]

**Slide 15 — Testing**
44 automated pytest tests against a real MySQL test database — **44/44
passed**. Plus a manual 29-step end-to-end demo flow, fully passed.
(See `TEST_RESULTS.md` for raw output.)

**Slide 16 — Deployment**
Environment-variable-driven configuration, ready for any Flask+MySQL host
(e.g. Railway). **Status:** deployment-ready; not deployed to a live URL
in this build session (no cloud credentials available) — state this
honestly rather than claiming a live link that doesn't exist.

**Slide 17 — Results & Limitations**
Results: every core feature works end-to-end, verified by tests.
Limitations: not yet deployed live, no load/browser testing performed,
quiz options not shuffled.

**Slide 18 — Future Scope & Conclusion**
Future: certificates, dark mode, CSV/PDF export, institution competitions,
PWA. Conclusion: a complete, understandable, working, tested gamified
environmental education platform built with a deliberately simple,
defendable technology stack.

---

**Presenter note:** If a live demo is possible, follow the Chapter-11-
style flow: register/login as student → complete lesson → take quiz →
complete challenge → leaderboard → logout → teacher login → admin login.
This exact flow was manually verified to work (see `TEST_RESULTS.md`).
