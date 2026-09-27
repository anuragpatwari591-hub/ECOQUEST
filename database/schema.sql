-- EcoQuest Database Schema (MySQL 8.0)
-- Run: mysql -u root -p < database/schema.sql

CREATE DATABASE IF NOT EXISTS ecoquest CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE ecoquest;

-- ---------------------------------------------------------------------
-- USERS  (students, teachers, admins share one table, distinguished by role)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    user_id         INT AUTO_INCREMENT PRIMARY KEY,
    name            VARCHAR(100) NOT NULL,
    email           VARCHAR(150) NOT NULL UNIQUE,
    password_hash   VARCHAR(255) NOT NULL,
    role            ENUM('student', 'teacher', 'admin') NOT NULL DEFAULT 'student',
    class_name      VARCHAR(50)  DEFAULT NULL,        -- e.g. 'BTech CSE 3rd Year' (students)
    institution     VARCHAR(150) DEFAULT NULL,
    total_xp        INT NOT NULL DEFAULT 0,
    current_streak  INT NOT NULL DEFAULT 0,
    longest_streak  INT NOT NULL DEFAULT 0,
    last_activity_date DATE DEFAULT NULL,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_users_role (role),
    INDEX idx_users_xp (total_xp)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- TOPICS  (the 6 environmental categories)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS topics (
    topic_id      INT AUTO_INCREMENT PRIMARY KEY,
    name          VARCHAR(100) NOT NULL UNIQUE,
    description   TEXT,
    icon          VARCHAR(50) DEFAULT '🌱',
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- LESSONS
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS lessons (
    lesson_id     INT AUTO_INCREMENT PRIMARY KEY,
    topic_id      INT NOT NULL,
    title         VARCHAR(150) NOT NULL,
    difficulty    ENUM('Beginner', 'Intermediate', 'Advanced') NOT NULL DEFAULT 'Beginner',
    introduction  TEXT,
    explanation   TEXT,
    key_points    TEXT,          -- newline-separated bullet points
    eco_tip       TEXT,
    xp_reward     INT NOT NULL DEFAULT 10,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (topic_id) REFERENCES topics(topic_id) ON DELETE CASCADE,
    INDEX idx_lessons_topic (topic_id)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- LESSON COMPLETIONS  (User N:M Lesson)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS lesson_completions (
    completion_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id       INT NOT NULL,
    lesson_id     INT NOT NULL,
    completed_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (lesson_id) REFERENCES lessons(lesson_id) ON DELETE CASCADE,
    UNIQUE KEY uq_user_lesson (user_id, lesson_id)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- QUIZZES
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS quizzes (
    quiz_id       INT AUTO_INCREMENT PRIMARY KEY,
    topic_id      INT NOT NULL,
    title         VARCHAR(150) NOT NULL,
    description   TEXT,
    created_by    INT DEFAULT NULL,      -- teacher/admin user_id who authored it
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (topic_id) REFERENCES topics(topic_id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE SET NULL,
    INDEX idx_quizzes_topic (topic_id)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- QUESTIONS
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS questions (
    question_id   INT AUTO_INCREMENT PRIMARY KEY,
    quiz_id       INT NOT NULL,
    question_text TEXT NOT NULL,
    FOREIGN KEY (quiz_id) REFERENCES quizzes(quiz_id) ON DELETE CASCADE,
    INDEX idx_questions_quiz (quiz_id)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- OPTIONS  (each question has exactly 4 options, one correct)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS options (
    option_id     INT AUTO_INCREMENT PRIMARY KEY,
    question_id   INT NOT NULL,
    option_text   VARCHAR(255) NOT NULL,
    is_correct    BOOLEAN NOT NULL DEFAULT FALSE,
    FOREIGN KEY (question_id) REFERENCES questions(question_id) ON DELETE CASCADE,
    INDEX idx_options_question (question_id)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- QUIZ ATTEMPTS
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS quiz_attempts (
    attempt_id    INT AUTO_INCREMENT PRIMARY KEY,
    user_id       INT NOT NULL,
    quiz_id       INT NOT NULL,
    score         INT NOT NULL DEFAULT 0,
    total_questions INT NOT NULL DEFAULT 0,
    xp_earned     INT NOT NULL DEFAULT 0,
    attempted_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (quiz_id) REFERENCES quizzes(quiz_id) ON DELETE CASCADE,
    INDEX idx_attempts_user (user_id),
    INDEX idx_attempts_quiz (quiz_id)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- QUIZ ANSWERS  (per-question answer within an attempt, for review screens)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS quiz_answers (
    answer_id     INT AUTO_INCREMENT PRIMARY KEY,
    attempt_id    INT NOT NULL,
    question_id   INT NOT NULL,
    selected_option_id INT DEFAULT NULL,
    is_correct    BOOLEAN NOT NULL DEFAULT FALSE,
    FOREIGN KEY (attempt_id) REFERENCES quiz_attempts(attempt_id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES questions(question_id) ON DELETE CASCADE,
    FOREIGN KEY (selected_option_id) REFERENCES options(option_id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- CHALLENGES
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS challenges (
    challenge_id  INT AUTO_INCREMENT PRIMARY KEY,
    title         VARCHAR(150) NOT NULL,
    description   TEXT,
    category      VARCHAR(100) DEFAULT NULL,   -- e.g. Waste Management, Water Conservation
    difficulty    ENUM('Easy', 'Medium', 'Hard') NOT NULL DEFAULT 'Easy',
    xp_reward     INT NOT NULL DEFAULT 20,
    is_active     BOOLEAN NOT NULL DEFAULT TRUE,
    created_by    INT DEFAULT NULL,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- CHALLENGE COMPLETIONS
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS challenge_completions (
    completion_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id       INT NOT NULL,
    challenge_id  INT NOT NULL,
    completed_on  DATE NOT NULL,
    xp_earned     INT NOT NULL DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (challenge_id) REFERENCES challenges(challenge_id) ON DELETE CASCADE,
    UNIQUE KEY uq_user_challenge_day (user_id, challenge_id, completed_on)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- BADGES
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS badges (
    badge_id      INT AUTO_INCREMENT PRIMARY KEY,
    name          VARCHAR(100) NOT NULL UNIQUE,
    description   TEXT,
    icon          VARCHAR(50) DEFAULT '🏅',
    criteria_type ENUM('lessons_completed', 'quizzes_completed', 'challenges_category',
                        'streak_days', 'total_xp') NOT NULL,
    criteria_value INT NOT NULL DEFAULT 1,
    criteria_category VARCHAR(100) DEFAULT NULL   -- used only for challenges_category
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- USER BADGES  (User N:M Badge)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS user_badges (
    user_badge_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id       INT NOT NULL,
    badge_id      INT NOT NULL,
    earned_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (badge_id) REFERENCES badges(badge_id) ON DELETE CASCADE,
    UNIQUE KEY uq_user_badge (user_id, badge_id)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- USER PROGRESS  (per-topic completion percentage, kept updated by the app)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS user_progress (
    progress_id     INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT NOT NULL,
    topic_id        INT NOT NULL,
    lessons_completed INT NOT NULL DEFAULT 0,
    total_lessons   INT NOT NULL DEFAULT 0,
    progress_percent INT NOT NULL DEFAULT 0,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (topic_id) REFERENCES topics(topic_id) ON DELETE CASCADE,
    UNIQUE KEY uq_user_topic (user_id, topic_id)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- ACTIVITY LOG  (drives the streak calculation and "recent activity" feed)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS activity_log (
    log_id        INT AUTO_INCREMENT PRIMARY KEY,
    user_id       INT NOT NULL,
    activity_type ENUM('lesson_completed', 'quiz_attempted', 'challenge_completed', 'badge_earned') NOT NULL,
    description   VARCHAR(255) NOT NULL,
    xp_change     INT NOT NULL DEFAULT 0,
    activity_date DATE NOT NULL,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_activity_user_date (user_id, activity_date)
) ENGINE=InnoDB;
