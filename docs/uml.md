# EcoQuest — UML Diagrams

These diagrams reflect the actual implemented modules (`routes/`, `utils/`)
rather than a generic OOP design, since the application is built as Flask
functions/blueprints rather than a class hierarchy. Where the project does
use classes (e.g. `Config`), that is shown too.

## 1. Class Diagram (Configuration + conceptual data classes)

```mermaid
classDiagram
    class Config {
        +SECRET_KEY: str
        +DB_HOST: str
        +DB_PORT: int
        +DB_USER: str
        +DB_PASSWORD: str
        +DB_NAME: str
        +XP_LESSON_COMPLETE: int
        +XP_CORRECT_ANSWER: int
        +XP_PERFECT_QUIZ_BONUS: int
        +XP_STREAK_7_DAY_BONUS: int
        +XP_PER_LEVEL: int
    }
    class TestConfig {
        +TESTING: bool
        +DB_NAME: str
    }
    TestConfig --|> Config

    class User {
        +user_id: int
        +name: str
        +email: str
        +password_hash: str
        +role: str
        +total_xp: int
        +current_streak: int
        +longest_streak: int
    }
    class Topic { +topic_id: int +name: str +description: str }
    class Lesson { +lesson_id: int +topic_id: int +title: str +xp_reward: int }
    class Quiz { +quiz_id: int +topic_id: int +title: str }
    class Question { +question_id: int +quiz_id: int +question_text: str }
    class Option { +option_id: int +question_id: int +is_correct: bool }
    class Challenge { +challenge_id: int +title: str +xp_reward: int }
    class Badge { +badge_id: int +name: str +criteria_type: str +criteria_value: int }

    Topic "1" --> "many" Lesson : contains
    Topic "1" --> "many" Quiz : contains
    Quiz "1" --> "many" Question : contains
    Question "1" --> "many" Option : contains
    User "many" --> "many" Badge : earns
```

*(`User`, `Topic`, `Lesson`, etc. are represented as MySQL rows/dict
records in the actual code, not Python classes — see `utils/database.py`
which returns plain `dict`s via `pymysql.cursors.DictCursor`. They are
shown here as classes purely for the conceptual data model, per usual UML
convention for ER-backed systems.)*

## 2. Sequence Diagram — Taking a Quiz

```mermaid
sequenceDiagram
    actor Student
    participant Flask as Flask (routes/quiz.py)
    participant DB as MySQL

    Student->>Flask: GET /quiz/3/start
    Flask->>DB: SELECT questions WHERE quiz_id=3
    DB-->>Flask: question rows
    Flask-->>Student: session[quiz_state] set, redirect to /quiz/question

    loop for each question
        Student->>Flask: GET /quiz/question
        Flask->>DB: SELECT question + options
        DB-->>Flask: rows
        Flask-->>Student: render quiz_question.html
        Student->>Flask: POST /quiz/question (option_id)
        Flask-->>Flask: store answer in session
    end

    Student->>Flask: (auto) GET /quiz/submit
    Flask->>DB: SELECT is_correct for each selected option
    Flask->>DB: INSERT quiz_attempts (score, xp_earned)
    Flask->>DB: INSERT quiz_answers (per question)
    Flask->>DB: UPDATE users SET total_xp += xp_earned
    Flask->>DB: INSERT activity_log
    Flask->>DB: check_and_award_badges()
    Flask-->>Student: render quiz_result.html
```

## 3. Activity Diagram — Lesson Completion → Gamification

```mermaid
flowchart TD
    Start([Student opens lesson]) --> Read[Read lesson content]
    Read --> Click[Click Mark Complete]
    Click --> Check{Already completed?}
    Check -- Yes --> Info[Show info message] --> End([End])
    Check -- No --> Insert[INSERT lesson_completions]
    Insert --> Progress[Recompute topic progress %]
    Progress --> XP[Award XP: UPDATE users.total_xp]
    XP --> Log[INSERT activity_log]
    Log --> Streak{Active yesterday?}
    Streak -- Yes --> Inc[streak += 1]
    Streak -- No, gap --> Reset[streak = 1]
    Inc --> SevenCheck{streak == 7?}
    Reset --> BadgeCheck
    SevenCheck -- Yes --> Bonus[+100 XP bonus] --> BadgeCheck[Check all badge criteria]
    SevenCheck -- No --> BadgeCheck
    BadgeCheck --> Award[INSERT user_badges for newly earned] --> Flash[Flash XP + badge messages]
    Flash --> End
```

## 4. Component Diagram

```mermaid
flowchart LR
    subgraph Presentation
        Templates[templates/*.html]
        Static[static/css, static/js]
    end
    subgraph Application
        Auth[routes/auth.py]
        StudentR[routes/student.py]
        QuizR[routes/quiz.py]
        ChallengeR[routes/challenge.py]
        TeacherR[routes/teacher.py]
        AdminR[routes/admin.py]
        AuthUtil[utils/auth.py]
        GameUtil[utils/gamification.py]
        DBUtil[utils/database.py]
    end
    subgraph Data
        MySQL[(MySQL: ecoquest)]
    end

    Templates --> Application
    Auth --> AuthUtil
    StudentR --> GameUtil
    QuizR --> GameUtil
    ChallengeR --> GameUtil
    GameUtil --> DBUtil
    Auth --> DBUtil
    StudentR --> DBUtil
    QuizR --> DBUtil
    ChallengeR --> DBUtil
    TeacherR --> DBUtil
    AdminR --> DBUtil
    DBUtil --> MySQL
```

## 5. Deployment Diagram

```mermaid
flowchart LR
    Dev[Developer machine] -- git push --> GitHub[(GitHub repository)]
    GitHub -- deploy --> Cloud[Cloud host, e.g. Railway]
    subgraph Cloud
        WSGI[gunicorn running app.py]
        EnvVars[Environment variables: SECRET_KEY, DB_*]
    end
    Cloud -- SQL over TCP --> ManagedDB[(Managed MySQL instance)]
    Browser[Student / Teacher / Admin browser] -- HTTPS --> Cloud
```
