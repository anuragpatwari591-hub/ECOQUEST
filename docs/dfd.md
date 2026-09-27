# EcoQuest — Data Flow Diagrams

These diagrams describe only processes, data stores and external entities
that actually exist in the implemented application.

## Level 0 (Context Diagram)

```mermaid
flowchart LR
    Student([Student])
    Teacher([Teacher])
    Admin([Admin])
    System[[EcoQuest System]]

    Student -- registers / logs in / completes lessons, quizzes, challenges --> System
    System -- dashboard, XP, badges, leaderboard, lesson & quiz content --> Student

    Teacher -- creates quizzes/questions/challenges, views performance --> System
    System -- class analytics, student data --> Teacher

    Admin -- manages users, topics, lessons, quizzes, challenges, badges --> System
    System -- platform statistics --> Admin
```

## Level 1 (Major Processes)

```mermaid
flowchart TB
    S([Student]) --> P1[1.0 Authenticate User]
    T([Teacher]) --> P1
    A([Admin]) --> P1
    P1 <--> D1[(users)]

    S --> P2[2.0 Manage Learning]
    P2 <--> D2[(topics / lessons / lesson_completions / user_progress)]

    S --> P3[3.0 Take Quiz]
    T --> P6[6.0 Author Content]
    P3 <--> D3[(quizzes / questions / options / quiz_attempts / quiz_answers)]

    S --> P4[4.0 Complete Challenge]
    P4 <--> D4[(challenges / challenge_completions)]

    P2 --> P5[5.0 Gamification Engine]
    P3 --> P5
    P4 --> P5
    P5 <--> D1
    P5 <--> D5[(badges / user_badges / activity_log)]

    P6 <--> D3
    P6 <--> D4

    T --> P7[7.0 View Analytics]
    A --> P7
    P7 <--> D1
    P7 <--> D2
    P7 <--> D3
    P7 <--> D4

    A --> P8[8.0 Manage Platform]
    P8 <--> D1
    P8 <--> D2
    P8 <--> D3
    P8 <--> D4
    P8 <--> D5
```

**Process descriptions:**

| # | Process | Description |
|---|---|---|
| 1.0 | Authenticate User | Register, login, logout, session/role checks |
| 2.0 | Manage Learning | Browse topics, read lessons, mark complete, recompute progress |
| 3.0 | Take Quiz | Navigate questions, submit answers, score, award XP |
| 4.0 | Complete Challenge | Mark a challenge done (once/day), award XP |
| 5.0 | Gamification Engine | Award XP, compute level, update streak, check badge criteria |
| 6.0 | Author Content | Teacher creates quizzes/questions/challenges |
| 7.0 | View Analytics | Teacher/Admin dashboards (aggregated SQL queries) |
| 8.0 | Manage Platform | Admin CRUD on users/topics/lessons/quizzes/challenges/badges |

A Level 2 diagram was not produced — none of the Level 1 processes are
complex enough to need further decomposition for this project's scope.
