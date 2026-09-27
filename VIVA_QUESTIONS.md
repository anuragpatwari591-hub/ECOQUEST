# EcoQuest — Viva Questions & Answers (100+)

Answers are written to be concise, accurate, and directly tied to how
EcoQuest actually implements each concept.

## A. Programming (Python) — 15

1. **What is Python and why was it used here?**
   Python is a high-level, interpreted, general-purpose language. It was
   used because Flask (the web framework) is Python-based and Python was
   already covered in the curriculum.

2. **What is a function? Give an example from the project.**
   A reusable named block of code. Example: `calculate_level(total_xp)` in
   `utils/gamification.py` takes XP and returns the level.

3. **What is the difference between a list and a tuple?**
   Lists are mutable (`[]`), tuples are immutable (`()`). The project uses
   tuples for fixed SQL parameter sets, e.g. `(user_id, lesson_id)`.

4. **What is a dictionary? Where is it used in this project?**
   A key-value data structure. `PyMySQL`'s `DictCursor` returns every
   database row as a Python `dict`, e.g. `user["total_xp"]`.

5. **What are conditional statements? Example from the code?**
   `if/elif/else` control flow. Example: role-based redirect after login in
   `routes/auth.py` (`if role == 'student': ... elif 'teacher': ...`).

6. **What are loops? Give an example.**
   `for`/`while` repeat a block. Example: `for badge in all_badges:` in
   `check_and_award_badges()` iterates every badge definition.

7. **What is exception handling and is it used here?**
   `try/except` catches runtime errors. The project relies on Flask's
   built-in error handlers (`@app.errorhandler(403/404/500)`) rather than
   scattering `try/except` everywhere, since most operations are simple
   parameterized queries.

8. **What is a module? Name modules used in EcoQuest.**
   A `.py` file that groups related code. Examples: `utils/database.py`,
   `utils/gamification.py`, `routes/auth.py`.

9. **What is a decorator? Where is it used?**
   A function that wraps another function to add behavior.
   `@role_required("student")` in `utils/auth.py` wraps view functions to
   enforce login/role checks before the view runs.

10. **What does `**kwargs`/`*args` do? Is it used here?**
    They collect extra positional/keyword arguments. Used inside the
    `login_required`/`role_required` decorators (`def wrapped(*args, **kwargs)`)
    so the decorator works on view functions with any signature.

11. **What is string formatting and where is it used?**
    f-strings build dynamic text, e.g.
    `f"Completed lesson: {lesson['title']}"` in `routes/student.py`.

12. **What is the difference between `==` and `is`?**
    `==` compares values; `is` compares object identity. The project uses
    `==` throughout (e.g. comparing `role` strings).

13. **What is a virtual environment and why use one?**
    An isolated Python installation per project (`venv`) so dependencies
    don't clash across projects. Used during development
    (`requirements.txt` lists exact versions).

14. **How are environment variables read in Python here?**
    Via `os.environ.get(...)` in `config.py`, loaded from a `.env` file
    using `python-dotenv`'s `load_dotenv()`.

15. **What is list/dict comprehension? Example?**
    A compact way to build a list/dict. Example:
    `names = [b["name"] for b in new_badges]` used in tests.

## B. Object-Oriented Programming — 10

16. **Does EcoQuest use classes?**
    Yes, but sparingly and where they add real value: `Config`/`TestConfig`
    in `config.py`. Most of the app is written as plain functions organized
    into modules/blueprints, which is simpler to reason about for a
    request/response web app than a deep class hierarchy.

17. **What is inheritance? Where is it used?**
    A class reusing/extending another's behavior. `TestConfig(Config)`
    inherits all of `Config`'s settings and overrides `DB_NAME`/`TESTING`.

18. **What is encapsulation?**
    Bundling data and the logic that operates on it, hiding internal
    details. `utils/gamification.py` encapsulates all XP/level/badge/streak
    logic behind a small function API (`award_xp`, `calculate_level`, …) so
    routes never manipulate XP directly.

19. **What is polymorphism? Is it used here?**
    Same interface, different behavior per type. Not heavily used in
    EcoQuest since the app doesn't need multiple interchangeable
    implementations of the same interface — using it here would be
    over-engineering for this project's scope.

20. **What is abstraction?**
    Exposing only what's necessary. `utils/database.py` abstracts raw
    PyMySQL connection handling behind `query_all`/`query_one`/`execute`,
    so route code never touches cursors directly.

21. **Why not build a full class-based domain model (User, Quiz, etc.)?**
    The app's data already has a clean relational shape in MySQL. Mapping
    every row to a Python object (an ORM-style model) would add an
    abstraction layer without a clear benefit at this scale, and would be
    harder to map directly to the SQL taught in the curriculum.

22. **What is a constructor?**
    A method that initializes an object, `__init__` in Python. Not
    explicitly used here since the project avoids custom classes beyond
    `Config`, which uses class attributes instead.

23. **What is method overriding?**
    A subclass redefining a parent method/attribute.
    `TestConfig.DB_NAME` overrides `Config.DB_NAME`'s default value.

24. **What is composition vs inheritance?**
    Composition builds functionality from smaller parts; inheritance
    extends a base type. EcoQuest favors composition — routes *use*
    `utils.gamification` and `utils.database` rather than inheriting from
    them.

25. **Why avoid deep class hierarchies in a student project?**
    Deep hierarchies are hard to trace and explain line-by-line in a viva.
    Flat, function-based modules with clear responsibilities are easier to
    defend and modify correctly under exam pressure.

## C. Database / SQL — 20

26. **What is a DBMS?**
    Software to create, manage and query databases. MySQL is the DBMS used.

27. **What is a primary key? Example?**
    A column uniquely identifying a row. `users.user_id` is the primary key
    of `users`.

28. **What is a foreign key? Example?**
    A column referencing another table's primary key.
    `lessons.topic_id` references `topics.topic_id`.

29. **What is normalization? To what normal form is this schema?**
    Organizing data to reduce redundancy. The schema is in 3NF — e.g.
    quiz options aren't repeated per attempt; they're stored once in
    `options` and referenced by `quiz_answers.selected_option_id`.

30. **What is a JOIN? Give an example from the project.**
    Combines rows from two+ tables on a related column.
    ```sql
    SELECT l.*, t.name AS topic_name FROM lessons l
    JOIN topics t ON l.topic_id = t.topic_id;
    ```

31. **Difference between INNER JOIN and LEFT JOIN?**
    INNER JOIN returns only matching rows; LEFT JOIN returns all rows from
    the left table even without a match (nulls for the right side). The
    dashboard uses LEFT JOIN so a topic with no progress row yet still
    shows (`COALESCE(up.progress_percent, 0)`).

32. **What does GROUP BY do? Example?**
    Aggregates rows sharing a value. Teacher dashboard:
    `GROUP BY t.topic_id, t.name` to compute average progress per topic.

33. **What does ORDER BY do? Example?**
    Sorts result rows. Leaderboard: `ORDER BY total_xp DESC`.

34. **What are aggregate functions? Examples used here?**
    Functions computing one value from many rows: `COUNT()`, `AVG()`, `SUM()`.
    Used for dashboard statistics, e.g. `COUNT(*)` for total students.

35. **What is an index? Why use one?**
    A data structure speeding up lookups on a column.
    `INDEX idx_users_xp (total_xp)` speeds up the leaderboard's ORDER BY.

36. **What is a UNIQUE constraint? Example?**
    Ensures no duplicate values in a column (or column combination).
    `UNIQUE (user_id, lesson_id)` on `lesson_completions` prevents
    completing the same lesson twice.

37. **What is referential integrity?**
    The guarantee that foreign keys always point to an existing row.
    Enforced by MySQL's `FOREIGN KEY ... REFERENCES` constraints.

38. **What is `ON DELETE CASCADE`?**
    Automatically deletes dependent rows when the referenced row is
    deleted. Deleting a topic cascades to delete its lessons and quizzes.

39. **What is a transaction? Are transactions used here?**
    A group of operations that succeed or fail together (ACID). The
    project runs with `autocommit=True` for simplicity since most writes
    are single-statement; multi-statement flows (e.g. quiz submission) are
    not wrapped in explicit transactions — a reasonable simplification at
    this scale, though a production system might wrap the attempt+answers
    insert in one transaction.

40. **What is a composite/window function? Example used?**
    `RANK() OVER (ORDER BY total_xp DESC)` computes each student's rank on
    the leaderboard without a separate subquery per row.

41. **How does the app prevent SQL injection?**
    Every query uses parameterized placeholders (`%s`) via PyMySQL, e.g.
    `query_one("SELECT * FROM users WHERE email = %s", (email,))` — never
    string concatenation of user input into SQL.

42. **What is `AUTO_INCREMENT`?**
    Automatically generates a unique, incrementing integer for a primary
    key column, e.g. `user_id INT AUTO_INCREMENT PRIMARY KEY`.

43. **What is an ENUM column? Example?**
    A column restricted to a fixed set of values.
    `role ENUM('student','teacher','admin')` in `users`.

44. **How would you retrieve a student's quiz history?**
    ```sql
    SELECT qa.*, q.title FROM quiz_attempts qa
    JOIN quizzes q ON qa.quiz_id = q.quiz_id
    WHERE qa.user_id = ? ORDER BY qa.attempted_at DESC;
    ```

45. **What is `COALESCE` used for here?**
    Returns the first non-null argument.
    `COALESCE(up.progress_percent, 0)` shows 0% instead of NULL when a
    student has no progress row for a topic yet.

46. **How many tables does the schema have, and why not fewer/more?**
    14 tables — enough to model users, content (topics/lessons/quizzes/
    questions/options/challenges/badges) and activity (completions,
    attempts, answers, progress, logs) without redundant or merged tables
    that would violate normalization.

47. **What is the difference between `DELETE` and `TRUNCATE`?**
    `DELETE` removes rows (optionally filtered, can be rolled back within
    a transaction, fires constraints row-by-row); `TRUNCATE` resets a whole
    table instantly. The test suite's `conftest.py` uses `DROP TABLE` +
    re-`CREATE` (via schema.sql) between tests rather than either, for a
    guaranteed-clean, migration-proof reset.

48. **How is many-to-many modeled between users and badges?**
    Through a junction table, `user_badges(user_id, badge_id)`, with a
    `UNIQUE(user_id, badge_id)` constraint preventing duplicate awards.

49. **What does `DictCursor` do, and why use it?**
    Makes PyMySQL return rows as `dict`s (`row["name"]`) instead of tuples
    (`row[0]`), which is far more readable in route code and Jinja2
    templates.

50. **How would you find the average quiz score per topic?**
    ```sql
    SELECT t.name, AVG(qa.score/qa.total_questions*100) AS avg_pct
    FROM topics t JOIN quizzes q ON t.topic_id=q.topic_id
    JOIN quiz_attempts qa ON q.quiz_id=qa.quiz_id
    GROUP BY t.topic_id, t.name;
    ```

## D. Web Fundamentals — 15

51. **What is the client-server model?**
    The browser (client) sends requests; the Flask server processes them
    and returns responses. EcoQuest's browser never talks to MySQL
    directly — always through Flask.

52. **What is HTTP? Name methods used in this project.**
    The protocol browsers and servers use to communicate. EcoQuest uses
    `GET` (view pages) and `POST` (submit forms, mutate data).

53. **What is the difference between GET and POST?**
    GET requests data and shouldn't change server state; POST submits data
    that changes state. All "complete lesson/quiz/challenge" actions use
    POST.

54. **What is an HTTP status code? Give examples used here.**
    A 3-digit response code. EcoQuest returns `200` (success), `302`
    (redirect, e.g. after login), `403` (forbidden, wrong role), `404`
    (not found).

55. **What is a session/cookie?**
    A session persists data (like `user_id`) across requests, backed by a
    signed cookie. `session["user_id"] = user["user_id"]` after login.

56. **What is HTML used for here?**
    Structuring page content — every page extends `templates/base.html`.

57. **What is CSS used for here?**
    Styling — `static/css/style.css` defines the green design system,
    cards, buttons, progress bars and responsive layout.

58. **What is JavaScript used for here?**
    Small UX enhancements: mobile nav toggle, auto-dismissing flash
    messages, highlighting the selected quiz option, and Chart.js graphs.
    The app functions even with JS disabled (forms are plain HTML).

59. **What is a form, and how does EcoQuest use forms?**
    An HTML element collecting user input and submitting it via GET/POST.
    E.g. the login form POSTs `email`/`password` to `/login`.

60. **What is responsive design?**
    CSS that adapts layout to screen size using media queries.
    `@media (max-width: 768px)` in `style.css` collapses the nav into a
    toggle menu on small screens.

61. **What is a template engine? Which one is used?**
    Jinja2 (bundled with Flask) — renders HTML with embedded Python-like
    expressions, e.g. `{% for lesson in lessons %}`.

62. **What is template inheritance?**
    Child templates extend a shared base
    (`{% extends "base.html" %}`) and fill named blocks
    (`{% block content %}`), avoiding repeated navbar/footer code.

63. **What is CORS, and does EcoQuest need it?**
    Cross-Origin Resource Sharing controls requests between different
    origins. Not needed here — EcoQuest is a single-origin server-rendered
    app, not a separate frontend/API pair.

64. **What is XSS, and how does the project guard against it?**
    Cross-Site Scripting — injecting malicious script into rendered pages.
    Jinja2 auto-escapes variables by default, so user-provided text (like a
    lesson title) is rendered safely rather than as executable HTML.

65. **What is a RESTful route, and does EcoQuest follow REST strictly?**
    REST models resources with URLs and HTTP verbs. EcoQuest is
    "REST-ish" — e.g. `/challenges/<id>/complete` — but prioritizes clear,
    readable routes over strict REST purity, appropriate for a
    server-rendered app rather than a public API.

## E. Flask — 15

66. **What is Flask?**
    A lightweight Python web framework used to define routes, handle
    requests/responses and render templates.

67. **What is a Flask blueprint, and why does EcoQuest use them?**
    A way to group related routes into a reusable component. EcoQuest has
    six blueprints (`auth`, `student`, `quiz`, `challenge`, `teacher`,
    `admin`) so each role/module's routes live in their own file.

68. **How is the Flask app created in this project?**
    Via an application factory, `create_app()` in `app.py`, which builds
    the app, loads config, registers blueprints and error handlers, then
    returns it — this pattern also makes `TestConfig` easy to inject for
    tests.

69. **What is `@app.route` / a route decorator?**
    Registers a URL pattern to a view function. E.g.
    `@bp.route("/login", methods=["GET", "POST"])`.

70. **How does Flask handle request data?**
    Via the `request` object — `request.form.get("email")` for form
    fields.

71. **What is `render_template`?**
    Renders a Jinja2 template file with given context variables, e.g.
    `render_template("student/dashboard.html", user=user, level=level)`.

72. **What is `redirect`/`url_for`?**
    `redirect()` sends the browser to another URL; `url_for()` builds that
    URL from a route's endpoint name so links don't break if a path
    changes, e.g. `redirect(url_for("student.dashboard"))`.

73. **What is `flash()`?**
    Queues a one-time message shown on the next rendered page (e.g.
    "Lesson completed! +10 XP"), read via `get_flashed_messages()` in
    `base.html`.

74. **How does EcoQuest manage app-wide config?**
    Through `config.py`'s `Config` class, loaded via
    `app.config.from_object(config_class)`, keeping secrets out of code.

75. **What is `g` in Flask, and how is it used here?**
    A per-request storage object. `utils/database.py` stores the MySQL
    connection on `g.db` so the same connection is reused within one
    request instead of opening a new one per query.

76. **What is `teardown_appcontext`?**
    Registers a function to run when the app context ends — used to close
    the database connection (`close_db`) after every request.

77. **How does Flask session-based login work here?**
    On successful login, `session["user_id"]`, `session["role"]`, and
    `session["name"]` are set; `@role_required` checks these on every
    protected route.

78. **What is an error handler in Flask?**
    A function registered for a status code, e.g.
    `@app.errorhandler(403)` renders a custom "Access Denied" page instead
    of Flask's default error page.

79. **How does the app avoid trusting client-submitted scores?**
    The quiz route never accepts a "score" from the client — it looks up
    `is_correct` for the submitted `option_id` server-side and computes the
    score itself in `routes/quiz.py`.

80. **Why use server-side session state for the in-progress quiz instead of localStorage?**
    Keeping quiz progress (`quiz_state`) in the Flask session means the
    server is always the source of truth and a user can't tamper with
    which questions they've "answered" via browser dev tools.

## F. Software Engineering — 15

81. **What is SDLC?**
    Software Development Life Cycle — the structured phases (requirements,
    design, implementation, testing, deployment, maintenance) followed to
    build software.

82. **Which SDLC model did this project follow?**
    Agile/incremental — built and verified in increments (schema → auth →
    student module → quiz/gamification → challenges → teacher/admin →
    testing → docs), each verified before moving to the next.

83. **What is an SRS?**
    Software Requirements Specification — documents what the system must
    do. See `docs/srs.md`.

84. **What is a DFD?**
    Data Flow Diagram — shows how data moves between processes, stores and
    external entities. See `docs/dfd.md`.

85. **What is an ER diagram?**
    Entity-Relationship diagram showing tables, attributes and
    relationships. See `docs/database.md`.

86. **What is UML, and which diagrams were made?**
    Unified Modeling Language. Class, sequence, activity, component and
    deployment diagrams were made — see `docs/uml.md`.

87. **What is unit testing vs integration testing? Which does EcoQuest have?**
    Unit tests check one function in isolation; integration tests check
    multiple components together. EcoQuest's pytest suite is closer to
    integration testing — it exercises routes + gamification logic +
    a real MySQL database together, which better matches how the app
    actually behaves in production.

88. **What is test-driven vs test-after development? Which was used here?**
    TDD writes tests before code; EcoQuest used test-after — the modules
    were implemented first, then verified with 44 automated tests plus a
    manual end-to-end script.

89. **What is regression testing?**
    Re-running tests after a change to confirm nothing broke. The pytest
    suite serves this role for future changes to EcoQuest.

90. **What is software maintainability, and how was it addressed here?**
    How easily software can be understood/modified. Addressed via
    blueprints (one file per module), a centralized `utils/gamification.py`
    for all game rules, and no duplicated business logic across routes.

91. **What is a risk in this project, and how was it mitigated?**
    Risk: business logic manipulated from the client (e.g. fake quiz
    score). Mitigation: all scoring/XP/level/badge logic runs server-side
    against the database, never trusting client input.

92. **What is version control, and how was Git used here?**
    Tracking code history over time. The project was committed in logical
    stages (schema, auth, modules, tests, docs) with descriptive commit
    messages.

93. **What is a feasibility study?**
    Assessing whether a project is technically/operationally/economically
    viable. EcoQuest is feasible: it uses free/open-source tools
    (Python, Flask, MySQL) that run on modest hardware.

94. **What is the difference between verification and validation?**
    Verification asks "did we build it right?" (tests passing);
    validation asks "did we build the right thing?" (does it solve the
    stated problem — disengaging environmental education). Both were
    addressed: verification via the 44 tests, validation via mapping every
    feature back to the original problem statement.

95. **What is technical debt, and does this project have any?**
    Shortcuts taken for speed that cost more to fix later. Known items:
    quiz option order isn't randomized, and multi-statement DB writes
    (e.g. quiz submission) aren't wrapped in explicit transactions — both
    documented honestly in `TODO.md` rather than hidden.

## G. Project-Specific — 20+

96. **Why EcoQuest? What problem does it solve?**
    Traditional environmental education is theoretical and disengaging.
    EcoQuest makes it interactive via gamified lessons, quizzes and
    real-world challenges, per the original problem statement.

97. **Why gamification specifically?**
    XP/levels/badges/streaks are proven engagement mechanics that reward
    consistent participation, which directly supports the goal of
    increasing sustained engagement with environmental topics.

98. **Why Flask over Django or Node.js/Express?**
    Flask is minimal and every request/response step is visible and
    explainable; Django's ORM/admin and Node's async event loop add
    concepts beyond what this project needs or what was taught.

99. **Why MySQL over MongoDB/Firebase?**
    The data is inherently relational (users → attempts → quizzes →
    questions → options, with clear foreign keys) — a relational database
    with normalized tables is the textbook-correct fit, and SQL is a
    required curriculum topic.

100. **Why not React/Vue for the frontend?**
     Server-rendered Jinja2 templates fully cover this app's needs (mostly
     forms and data display) without a build pipeline, a second language
     (JSX), or client-side state management the app doesn't require.

101. **How does XP work end-to-end?**
     A route (e.g. lesson completion) calls
     `award_xp(user_id, amount, activity_type, description)`, which
     updates `users.total_xp`, logs the event in `activity_log`, updates
     the streak, and checks for newly-earned badges — all in one function
     so every XP source behaves consistently.

102. **How does level calculation work?**
     `level = floor(total_xp / 100) + 1`, computed in
     `calculate_level()` — always derived from stored XP, never stored
     redundantly, so it can never go stale.

103. **How does the leaderboard work?**
     A single SQL query ranks all students by `total_xp DESC` using the
     `RANK()` window function — no application-side sorting needed.

104. **How are badges awarded?**
     `check_and_award_badges()` loops over every badge definition,
     evaluates its `criteria_type` (lessons completed, quizzes completed,
     challenges in a category, streak days, or total XP) against the
     student's actual data, and inserts into `user_badges` for anything
     newly satisfied — `INSERT IGNORE` plus a UNIQUE constraint guarantees
     no duplicate awards even under a race.

105. **How does authentication work?**
     Werkzeug's `generate_password_hash`/`check_password_hash` (scrypt)
     hash and verify passwords; a successful login stores `user_id`/`role`
     in the Flask session.

106. **How are roles enforced?**
     The `@role_required(*roles)` decorator checks `session["role"]`
     against the allowed roles for that route and returns HTTP 403 if it
     doesn't match, before the view function body ever runs.

107. **How does topic progress work?**
     `update_topic_progress()` recomputes
     `lessons_completed / total_lessons * 100` from the actual
     `lesson_completions` rows every time a lesson is completed, and
     upserts the result into `user_progress` — so it's always accurate,
     not incrementally (and fallibly) adjusted.

108. **How does the daily streak work?**
     `update_streak()` compares `last_activity_date` to today: same day →
     unchanged; yesterday → +1; otherwise → resets to 1. Simple and easy
     to explain, per the project's own constraint to keep gamification
     logic viva-defendable.

109. **How is duplicate challenge completion prevented?**
     A `UNIQUE (user_id, challenge_id, completed_on)` constraint on
     `challenge_completions`, backed by an explicit existence check in the
     route before inserting.

110. **What are the platform's three roles and their permissions?**
     Student (learn/play/earn), Teacher (author content, view class
     analytics), Admin (manage all users and content) — enforced via
     `role_required` on every protected route.

111. **What are the six environmental topics covered?**
     Climate Change, Pollution, Waste Management, Water Conservation,
     Renewable Energy, Biodiversity — see `database/seed.sql`.

112. **What happens if a student answers a question without selecting an option?**
     The quiz form's option inputs are `required` client-side; if
     bypassed, the server records `selected_option_id = None` and treats
     the answer as incorrect (`is_correct = False`), so scoring can't be
     broken by skipping the client validation.

113. **What are the project's known limitations?**
     No live cloud deployment yet, no automated browser/UI testing, quiz
     options aren't shuffled, and multi-step quiz submission isn't wrapped
     in a single DB transaction — all listed honestly in
     `PROJECT_STATUS.md`/`TODO.md`.

114. **What is the future scope of this project?**
     Certificates, dark mode, CSV/PDF export, institution-level
     competitions, and PWA support — explicitly optional and not built in
     this session.

115. **How would you demo this project end-to-end in 5 minutes?**
     Register/login as a student → complete a lesson (show XP increase) →
     take a quiz (show scoring + badge) → complete a challenge → check the
     leaderboard/progress page → log out → log in as teacher (show class
     analytics) → log in as admin (show platform stats).

116. **How would you explain "not using AI/ML" if asked why?**
     "The selected architecture fulfills the requirements while remaining
     maintainable, understandable and appropriate for the project's scope
     and our technical expertise" — AI/ML would not solve this project's
     actual problem (making environmental education more engaging) and
     would be difficult to justify or defend as a B.Tech-level
     implementation.

117. **Why is `.env` never committed to Git?**
     It holds real secrets (DB password, Flask `SECRET_KEY`). Only
     `.env.example` (placeholder values) is committed; `.env` is listed in
     `.gitignore`.

118. **How is the project tested without a public deployment?**
     Locally: 44 pytest tests against a real MySQL test database, plus a
     manual HTTP-level demo-flow script against the live local dev server
     — both actually executed, not simulated.

119. **What would you change if you had more time?**
     Wrap quiz submission in an explicit DB transaction, add automated
     browser tests, shuffle quiz options, and deploy to a live host.

120. **What is the single most important design decision in this project, and why?**
     Keeping every gamification rule (XP, levels, badges, streaks) server-
     side and centralized in `utils/gamification.py` — it guarantees
     correctness (nothing can be faked from the browser) and makes the
     whole reward system explainable from one file in a viva.
