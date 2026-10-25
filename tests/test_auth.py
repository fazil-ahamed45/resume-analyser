from app.models import User


def test_user_registration(client, db_session):
    res = client.post(
        "/register",
        data={
            "full_name": "Charlie Davis",
            "email": "charlie@example.com",
            "password": "Password123!",
            "confirm_password": "Password123!",
            "experience_level": "fresher",
            "target_role": "Python Developer Intern",
            "ai_consent": True,
        },
        follow_redirects=True,
    )
    assert res.status_code == 200
    assert b"Account created successfully" in res.data

    user = User.query.filter_by(email="charlie@example.com").first()
    assert user is not None
    assert user.full_name == "Charlie Davis"
    assert user.check_password("Password123!") is True
    assert user.password_hash != "Password123!"  # Securely hashed


def test_duplicate_email_registration_fails(client, registered_user):
    res = client.post(
        "/register",
        data={
            "full_name": "Another Alice",
            "email": "alice@example.com",
            "password": "Password123!",
            "confirm_password": "Password123!",
            "experience_level": "fresher",
            "target_role": "Python Developer Intern",
        },
        follow_redirects=True,
    )
    assert res.status_code == 200
    assert b"already exists" in res.data


def test_login_success_and_logout(client, registered_user):
    # Valid login
    login_res = client.post(
        "/login",
        data={"email": "alice@example.com", "password": "Secret1234!"},
        follow_redirects=True,
    )
    assert login_res.status_code == 200
    assert b"Welcome back, Alice" in login_res.data

    # Logout
    logout_res = client.get("/logout", follow_redirects=True)
    assert logout_res.status_code == 200
    assert b"You have been signed out" in logout_res.data


def test_login_invalid_password(client, registered_user):
    res = client.post(
        "/login",
        data={"email": "alice@example.com", "password": "WrongPassword999"},
        follow_redirects=True,
    )
    assert res.status_code == 200
    assert b"Invalid email or password" in res.data


def test_protected_routes_redirect_unauthenticated(client):
    protected_urls = [
        "/dashboard",
        "/resumes/upload",
        "/resumes",
        "/career/match",
        "/career/recommendations",
        "/career/roadmap",
        "/career/interview",
        "/profile",
    ]
    for url in protected_urls:
        res = client.get(url, follow_redirects=False)
        assert res.status_code == 302
        assert "/login" in res.headers["Location"]
