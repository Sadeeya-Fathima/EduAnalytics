
import pytest
from werkzeug.security import generate_password_hash

from app import create_app
from app.extensions import db
from app.models import Institution, User


@pytest.fixture
def app():
    app = create_app({
        "TESTING": True,
        "SECRET_KEY": "test-secret-key",
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": True,
    })

    with app.app_context():
        db.create_all()

        institution = Institution(name="Test Institution")
        db.session.add(institution)
        db.session.flush()

        user = User(
            userid="TEST001",
            email="teacher@example.com",
            institution_id=institution.id,
            first_name="Test",
            last_name="Teacher",
            role="educator",
            status="active",
            password=generate_password_hash("CorrectPassword123!"),
        )
        db.session.add(user)
        db.session.commit()

    yield app

    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def get_csrf_token(client):
    response = client.get("/auth/login")
    assert response.status_code == 200

    html = response.get_data(as_text=True)
    marker = 'name="csrf_token" value="'
    assert marker in html

    return html.split(marker, 1)[1].split('"', 1)[0]


def test_login_page_loads(client):
    response = client.get("/auth/login")

    assert response.status_code == 200
    assert b"EduAnalytics" in response.data


def test_valid_login(client):
    token = get_csrf_token(client)

    response = client.post(
        "/auth/login",
        data={
            "userid": "TEST001",
            "password": "CorrectPassword123!",
            "csrf_token": token,
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")

def test_invalid_password_is_rejected(client):
    token = get_csrf_token(client)

    response = client.post(
        "/auth/login",
        data={
            "userid": "TEST001",
            "password": "WrongPassword!",
            "csrf_token": token,
        },
    )

    assert response.status_code == 401
    assert b"Invalid user ID or password" in response.data

def test_inactive_user_cannot_login(client, app):
    with app.app_context():
        user = db.session.get(User, "TEST001")
        user.status = "inactive"
        db.session.commit()

    token = get_csrf_token(client)

    response = client.post(
        "/auth/login",
        data={
            "userid": "TEST001",
            "password": "CorrectPassword123!",
            "csrf_token": token,
        },
    )

    assert response.status_code == 401
    assert b"account is inactive" in response.data

def test_login_rejects_missing_csrf_token(client):
    response = client.post(
        "/auth/login",
        data={
            "userid": "TEST001",
            "password": "CorrectPassword123!",
        },
    )

    assert response.status_code == 400

def test_logout_requires_authentication(client):
    token = get_csrf_token(client)

    response = client.post(
        "/auth/logout",
        data={"csrf_token": token},
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/auth/login")

def test_authenticated_user_can_logout(client):
    # Get a token before login.
    token = get_csrf_token(client)

    login_response = client.post(
        "/auth/login",
        data={
            "userid": "TEST001",
            "password": "CorrectPassword123!",
            "csrf_token": token,
        },
    )
    assert login_response.status_code == 302

    # The CSRF token is stored in the session and remains valid after login.
    # Reuse the token rather than requesting the login page again.
    logout_response = client.post(
        "/auth/logout",
        data={"csrf_token": token},
    )
    assert logout_response.status_code == 302
    assert "/auth/login" in logout_response.headers["Location"]

    # After logout, the protected home page should redirect to login.
    home_response = client.get("/")
    assert home_response.status_code == 302
    assert "/auth/login" in home_response.headers["Location"]


def test_deactivated_user_loses_existing_session(client, app):
    # Log in while the educator account is active.
    token = get_csrf_token(client)

    login_response = client.post(
        "/auth/login",
        data={
            "userid": "TEST001",
            "password": "CorrectPassword123!",
            "csrf_token": token,
        },
    )
    assert login_response.status_code == 302

    # Simulate an administrator deactivating the account.
    with app.app_context():
        user = db.session.get(User, "TEST001")
        user.status = "inactive"
        db.session.commit()

    # The existing session should no longer access the protected home page.
    response = client.get("/")

    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]
