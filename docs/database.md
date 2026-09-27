# EcoQuest — Database Design

MySQL 8, `utf8mb4`, InnoDB (for foreign key support). Full DDL:
[`database/schema.sql`](../database/schema.sql). Demo data:
[`database/seed.sql`](../database/seed.sql).

## 1. Tables (14)

| Table | Purpose |
|---|---|
| `users` | Students, teachers and admins (single table, `role` enum) |
| `topics` | The 6 environmental categories |
| `lessons` | Lesson content per topic |
| `lesson_completions` | Which student completed which lesson |
| `quizzes` | One quiz per topic (or more) |
| `questions` | Questions belonging to a quiz |
| `options` | 4 options per question, one `is_correct` |
| `quiz_attempts` | A student's attempt at a quiz (score, XP earned) |
| `quiz_answers` | Per-question answer within an attempt (for review screens) |
| `challenges` | Real-world eco-challenges |
| `challenge_completions` | Which student completed which challenge, on which day |
| `badges` | Badge definitions and unlock criteria |
| `user_badges` | Which student has earned which badge |
| `user_progress` | Cached per-topic completion percentage per student |
| `activity_log` | Every XP-earning event (drives streaks + "recent activity") |

## 2. Entity-Relationship Diagram

```mermaid
erDiagram
    USERS ||--o{ LESSON_COMPLETIONS : completes
    USERS ||--o{ QUIZ_ATTEMPTS : attempts
    USERS ||--o{ CHALLENGE_COMPLETIONS : completes
    USERS ||--o{ USER_BADGES : earns
    USERS ||--o{ USER_PROGRESS : tracks
    USERS ||--o{ ACTIVITY_LOG : generates
    USERS ||--o{ QUIZZES : authors
    USERS ||--o{ CHALLENGES : authors

    TOPICS ||--o{ LESSONS : contains
    TOPICS ||--o{ QUIZZES : contains
    TOPICS ||--o{ USER_PROGRESS : "tracked in"

    LESSONS ||--o{ LESSON_COMPLETIONS : "completed via"

    QUIZZES ||--o{ QUESTIONS : contains
    QUIZZES ||--o{ QUIZ_ATTEMPTS : "attempted via"

    QUESTIONS ||--o{ OPTIONS : contains
    QUESTIONS ||--o{ QUIZ_ANSWERS : "answered via"

    QUIZ_ATTEMPTS ||--o{ QUIZ_ANSWERS : contains
    OPTIONS ||--o{ QUIZ_ANSWERS : "selected as"

    CHALLENGES ||--o{ CHALLENGE_COMPLETIONS : "completed via"

    BADGES ||--o{ USER_BADGES : "awarded as"

    USERS {
        int user_id PK
        varchar name
        varchar email UK
        varchar password_hash
        enum role
        varchar class_name
        varchar institution
        int total_xp
        int current_streak
        int longest_streak
        date last_activity_date
    }

    TOPICS {
        int topic_id PK
        varchar name UK
        text description
        varchar icon
    }

    LESSONS {
        int lesson_id PK
        int topic_id FK
        varchar title
        enum difficulty
        text introduction
        text explanation
        text key_points
        text eco_tip
        int xp_reward
    }

    QUIZZES {
        int quiz_id PK
        int topic_id FK
        varchar title
        text description
        int created_by FK
    }

    QUESTIONS {
        int question_id PK
        int quiz_id FK
        text question_text
    }

    OPTIONS {
        int option_id PK
        int question_id FK
        varchar option_text
        boolean is_correct
    }

    QUIZ_ATTEMPTS {
        int attempt_id PK
        int user_id FK
        int quiz_id FK
        int score
        int total_questions
        int xp_earned
    }

    QUIZ_ANSWERS {
        int answer_id PK
        int attempt_id FK
        int question_id FK
        int selected_option_id FK
        boolean is_correct
    }

    CHALLENGES {
        int challenge_id PK
        varchar title
        text description
        varchar category
        enum difficulty
        int xp_reward
        boolean is_active
        int created_by FK
    }

    CHALLENGE_COMPLETIONS {
        int completion_id PK
        int user_id FK
        int challenge_id FK
        date completed_on
        int xp_earned
    }

    BADGES {
        int badge_id PK
        varchar name UK
        text description
        enum criteria_type
        int criteria_value
        varchar criteria_category
    }

    USER_BADGES {
        int user_badge_id PK
        int user_id FK
        int badge_id FK
    }

    USER_PROGRESS {
        int progress_id PK
        int user_id FK
        int topic_id FK
        int lessons_completed
        int total_lessons
        int progress_percent
    }

    LESSON_COMPLETIONS {
        int completion_id PK
        int user_id FK
        int lesson_id FK
    }

    ACTIVITY_LOG {
        int log_id PK
        int user_id FK
        enum activity_type
        varchar description
        int xp_change
        date activity_date
    }
```

## 3. Cardinality Summary

| Relationship | Cardinality |
|---|---|
| User → QuizAttempt | 1 : N |
| Quiz → Question | 1 : N |
| Question → Option | 1 : N (exactly 4 in practice) |
| Topic → Lesson | 1 : N |
| Topic → Quiz | 1 : N |
| User → ChallengeCompletion | 1 : N |
| Challenge → ChallengeCompletion | 1 : N |
| User ↔ Badge | N : M (via `user_badges`) |
| User → UserProgress | 1 : N (one row per topic) |
| User ↔ Lesson | N : M (via `lesson_completions`) |

## 4. Key Design Decisions

- **Single `users` table with a `role` enum** rather than separate
  Student/Teacher/Admin tables — all three share the same core attributes
  (name, email, password) and this avoids duplicate auth logic. Role-only
  fields (`total_xp`, `current_streak`, …) are simply `0`/`NULL` for
  teachers and admins.
- **`user_progress` is a cache, not a source of truth** — it is
  recalculated from `lesson_completions` every time a lesson is completed
  (`utils/gamification.update_topic_progress`), so it can never silently
  drift from the underlying completion data; it exists purely so the
  dashboard doesn't need an expensive join+aggregate on every page load.
- **`UNIQUE (user_id, lesson_id)`** on `lesson_completions` and
  **`UNIQUE (user_id, challenge_id, completed_on)`** on
  `challenge_completions` enforce "can't complete the same lesson twice"
  and "can't complete the same challenge more than once per day" at the
  database level, not just in application code.
- **`ON DELETE CASCADE`** on child tables (lessons, questions, options,
  completions, etc.) keeps the database consistent if a topic/quiz/user is
  removed, without requiring manual cleanup code.
- **Indexes** on foreign keys and on `users.total_xp` (used by the
  leaderboard's `ORDER BY total_xp DESC`) keep the common queries fast even
  as data grows, without needing a caching layer.

## 5. Example Queries (also used verbatim in the application code)

```sql
-- Leaderboard
SELECT name, total_xp, RANK() OVER (ORDER BY total_xp DESC) AS rnk
FROM users WHERE role = 'student' ORDER BY total_xp DESC;

-- A student's topic-wise progress
SELECT t.name, COALESCE(up.progress_percent, 0) AS progress_percent
FROM topics t
LEFT JOIN user_progress up ON t.topic_id = up.topic_id AND up.user_id = ?
ORDER BY t.topic_id;

-- Average quiz score per quiz (teacher dashboard)
SELECT q.title, AVG(qa.score / qa.total_questions * 100) AS avg_pct
FROM quizzes q LEFT JOIN quiz_attempts qa ON q.quiz_id = qa.quiz_id
GROUP BY q.quiz_id, q.title;
```
