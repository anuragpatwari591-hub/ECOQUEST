"""Tests for registration, login, logout and role-based authorization."""
from utils.database import query_one


def test_register_success(client):
    response = client.post("/register", data={
        "name": "New Student", "email": "new@test.com",
        "password": "abcdef", "confirm_password": "abcdef",
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Registration successful" in response.data


def test_register_duplicate_email_rejected(client):
    client.post("/register", data={
        "name": "A", "email": "dupe@test.com",
        "password": "abcdef", "confirm_password": "abcdef",
    })
    response = client.post("/register", data={
        "name": "B", "email": "dupe@test.com",
        "password": "abcdef", "confirm_password": "abcdef",
    })
    assert b"already exists" in response.data


def test_register_password_mismatch_rejected(client):
    response = client.post("/register", data={
        "name": "C", "email": "mismatch@test.com",
        "password": "abcdef", "confirm_password": "different",
    })
    assert b"do not match" in response.data


def test_password_is_hashed_not_plaintext(app, client):
    client.post("/register", data={
        "name": "D", "email": "hashcheck@test.com",
        "password": "plaintextpassword", "confirm_password": "plaintextpassword",
    })
    with app.app_context():
        user = query_one("SELECT password_hash FROM users WHERE email = %s", ("hashcheck@test.com",))
    assert user["password_hash"] != "plaintextpassword"
    assert user["password_hash"].startswith("scrypt:") or user["password_hash"].startswith("pbkdf2:")


def test_login_valid_credentials(client):
    response = client.post("/login", data={"email": "student@test.com", "password": "password123"}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Welcome back" in response.data


def test_login_invalid_password(client):
    response = client.post("/login", data={"email": "student@test.com", "password": "wrongpass"})
    assert b"Invalid email or password" in response.data


def test_login_nonexistent_email(client):
    response = client.post("/login", data={"email": "nobody@test.com", "password": "whatever"})
    assert b"Invalid email or password" in response.data


def test_logout_clears_session(student_client):
    student_client.get("/logout")
    response = student_client.get("/student/dashboard", follow_redirects=False)
    assert response.status_code == 302  # redirected to login


def test_student_blocked_from_admin(student_client):
    response = student_client.get("/admin/dashboard")
    assert response.status_code == 403


def test_student_blocked_from_teacher(student_client):
    response = student_client.get("/teacher/dashboard")
    assert response.status_code == 403


def test_teacher_blocked_from_admin(teacher_client):
    response = teacher_client.get("/admin/dashboard")
    assert response.status_code == 403


def test_admin_can_access_admin_dashboard(admin_client):
    response = admin_client.get("/admin/dashboard")
    assert response.status_code == 200


def test_admin_blocked_from_student_dashboard(admin_client):
    response = admin_client.get("/student/dashboard")
    assert response.status_code == 403


def test_unauthenticated_user_redirected_to_login(client):
    response = client.get("/student/dashboard", follow_redirects=False)
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]
