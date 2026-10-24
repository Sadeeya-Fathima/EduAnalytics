
from flask import Flask

from app.auth.decorators import role_required
from flask_login import LoginManager
from app.extensions import db

from app import create_app
from app.models import Institution, User
from werkzeug.security import generate_password_hash


def test_admin_can_access_admin_route():
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY="test-secret-key",
        WTF_CSRF_ENABLED=False,
    )
    test_login_manager = LoginManager()
    test_login_manager.init_app(app)

    class TestUser:
        is_authenticated = True
        role = "admin"

        def get_id(self):
            return "admin001"

    @test_login_manager.user_loader
    def load_user(user_id):
        return TestUser() if user_id == "admin001" else None

    @app.route("/admin")
    @role_required("admin")
    def admin_page():
        return "Admin access granted"

    client = app.test_client()

    with client:
        with client.session_transaction() as session:
            session["_user_id"] = "admin001"
            session["_fresh"] = True

        response = client.get("/admin")

    assert response.status_code == 200
    assert response.get_data(as_text=True) == "Admin access granted"

def test_educator_cannot_access_admin_route():
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY="test-secret-key",
        WTF_CSRF_ENABLED=False,
    )

    test_login_manager = LoginManager()
    test_login_manager.init_app(app)

    class TestUser:
        is_authenticated = True
        role = "educator"

        def get_id(self):
            return "teacher001"

    @test_login_manager.user_loader
    def load_user(user_id):
        return TestUser() if user_id == "teacher001" else None

    @app.route("/admin")
    @role_required("admin")
    def admin_page():
        return "Admin access granted"

    client = app.test_client()

    with client:
        with client.session_transaction() as session:
            session["_user_id"] = "teacher001"
            session["_fresh"] = True

        response = client.get("/admin")

    assert response.status_code == 403

def test_unauthenticated_user_is_redirected_from_educator_management():
    app = create_app({
        "TESTING": True,
        "SECRET_KEY": "test-secret-key",
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })

    client = app.test_client()
    response = client.get("/admin/educators")

    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]

def test_educator_is_forbidden_from_educator_management():
    app = create_app({
        "TESTING": True,
        "SECRET_KEY": "test-secret-key",
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })

    with app.app_context():
        institution = Institution(name="Test Institution")
        db.session.add(institution)
        db.session.flush()

        educator = User(
            userid="TEACHER001",
            email="teacher@example.com",
            institution_id=institution.id,
            first_name="Test",
            last_name="Educator",
            role="educator",
            status="active",
            password=generate_password_hash("TestPassword123!"),
        )
        db.session.add(educator)
        db.session.commit()

    client = app.test_client()

    with client:
        with client.session_transaction() as session:
            session["_user_id"] = "TEACHER001"
            session["_fresh"] = True

        response = client.get("/admin/educators")

        print("Status:", response.status_code)
        print("Redirect location:", response.headers.get("Location"))

    assert response.status_code == 403

def test_admin_can_access_educator_management():
    app = create_app({
        "TESTING": True,
        "SECRET_KEY": "test-secret-key",
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })

    with app.app_context():
        institution = Institution(name="Test Institution")
        db.session.add(institution)
        db.session.flush()

        admin = User(
            userid="ADMIN001",
            email="admin@example.com",
            institution_id=institution.id,
            first_name="Test",
            last_name="Admin",
            role="admin",
            status="active",
            password=generate_password_hash("TestPassword123!"),
        )
        db.session.add(admin)
        db.session.commit()

    client = app.test_client()

    with client:
        with client.session_transaction() as session:
            session["_user_id"] = "ADMIN001"
            session["_fresh"] = True

        response = client.get("/admin/educators")
        print("Status:", response.status_code)
        print("Redirect location:", response.headers.get("Location"))

    assert response.status_code == 200
    assert b"Educator Management" in response.data

def test_admin_can_create_educator_account():
    app = create_app({
        "TESTING": True,
        "SECRET_KEY": "test-secret-key",
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
    })

    with app.app_context():
        institution = Institution(name="Test Institution")
        db.session.add(institution)
        db.session.flush()
        institution_id = institution.id

        admin = User(
            userid="ADMIN001",
            email="admin@example.com",
            institution_id=institution_id,
            first_name="Test",
            last_name="Admin",
            role="admin",
            status="active",
            password=generate_password_hash("AdminPassword123!"),
        )
        db.session.add(admin)
        db.session.commit()

    client = app.test_client()

    with client:
        with client.session_transaction() as session:
            session["_user_id"] = "ADMIN001"
            session["_fresh"] = True

        response = client.post(
            "/admin/educators/create",
            data={
                "userid": "TEACHER002",
                "first_name": "New",
                "last_name": "Educator",
                "email": "new.educator@example.com",
                "title": "Lecturer",
                "institution_id": str(institution_id),
                "password": "EducatorPassword123!",
                "confirm_password": "EducatorPassword123!",
            },
        )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/admin/educators")

    with app.app_context():
        educator = db.session.get(User, "TEACHER002")

        assert educator is not None
        assert educator.role == "educator"
        assert educator.status == "active"
        assert educator.email == "new.educator@example.com"
        assert educator.password != "EducatorPassword123!"
        assert educator.password.startswith("scrypt:")

def test_duplicate_educator_userid_is_rejected():
    app = create_app({
        "TESTING": True,
        "SECRET_KEY": "test-secret-key",
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
    })

    with app.app_context():
        institution = Institution(name="Test Institution")
        db.session.add(institution)
        db.session.flush()

        admin = User(
            userid="ADMIN001",
            email="admin@example.com",
            institution_id=institution.id,
            first_name="Test",
            last_name="Admin",
            role="admin",
            status="active",
            password=generate_password_hash("AdminPassword123!"),
        )
        existing = User(
            userid="TEACHER001",
            email="teacher@example.com",
            institution_id=institution.id,
            first_name="Existing",
            last_name="Educator",
            role="educator",
            status="active",
            password=generate_password_hash("TeacherPassword123!"),
        )
        db.session.add_all([admin, existing])
        db.session.commit()
        institution_id = institution.id

    client = app.test_client()

    with client:
        with client.session_transaction() as session:
            session["_user_id"] = "ADMIN001"
            session["_fresh"] = True

        response = client.post(
            "/admin/educators/create",
            data={
                "userid": "TEACHER001",
                "first_name": "New",
                "last_name": "Educator",
                "email": "new@example.com",
                "institution_id": str(institution_id),
                "password": "EducatorPassword123!",
                "confirm_password": "EducatorPassword123!",
            },
        )

    assert response.status_code == 302

    with app.app_context():
        assert User.query.filter_by(userid="TEACHER001").count() == 1

def test_duplicate_educator_email_is_rejected():
    app = create_app({
        "TESTING": True,
        "SECRET_KEY": "test-secret-key",
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
    })

    with app.app_context():
        institution = Institution(name="Test Institution")
        db.session.add(institution)
        db.session.flush()

        admin = User(
            userid="ADMIN001",
            email="admin@example.com",
            institution_id=institution.id,
            first_name="Test",
            last_name="Admin",
            role="admin",
            status="active",
            password=generate_password_hash("AdminPassword123!"),
        )
        existing = User(
            userid="TEACHER001",
            email="teacher@example.com",
            institution_id=institution.id,
            first_name="Existing",
            last_name="Educator",
            role="educator",
            status="active",
            password=generate_password_hash("TeacherPassword123!"),
        )
        db.session.add_all([admin, existing])
        db.session.commit()
        institution_id = institution.id

    client = app.test_client()

    with client:
        with client.session_transaction() as session:
            session["_user_id"] = "ADMIN001"
            session["_fresh"] = True

        response = client.post(
            "/admin/educators/create",
            data={
                "userid": "TEACHER002",
                "first_name": "New",
                "last_name": "Educator",
                "email": "teacher@example.com",
                "institution_id": str(institution_id),
                "password": "EducatorPassword123!",
                "confirm_password": "EducatorPassword123!",
            },
        )

    assert response.status_code == 302

    with app.app_context():
        assert User.query.filter_by(userid="TEACHER002").first() is None

def test_mismatched_educator_passwords_are_rejected():
    app = create_app({
        "TESTING": True,
        "SECRET_KEY": "test-secret-key",
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
    })

    with app.app_context():
        institution = Institution(name="Test Institution")
        db.session.add(institution)
        db.session.flush()

        admin = User(
            userid="ADMIN001",
            email="admin@example.com",
            institution_id=institution.id,
            first_name="Test",
            last_name="Admin",
            role="admin",
            status="active",
            password=generate_password_hash("AdminPassword123!"),
        )
        db.session.add(admin)
        db.session.commit()
        institution_id = institution.id

    client = app.test_client()

    with client:
        with client.session_transaction() as session:
            session["_user_id"] = "ADMIN001"
            session["_fresh"] = True

        response = client.post(
            "/admin/educators/create",
            data={
                "userid": "TEACHER002",
                "first_name": "New",
                "last_name": "Educator",
                "email": "new@example.com",
                "institution_id": str(institution_id),
                "password": "EducatorPassword123!",
                "confirm_password": "DifferentPassword123!",
            },
        )

    assert response.status_code == 302

    with app.app_context():
        assert User.query.filter_by(userid="TEACHER002").first() is None

def test_invalid_institution_is_rejected():
    app = create_app({
        "TESTING": True,
        "SECRET_KEY": "test-secret-key",
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
    })

    with app.app_context():
        institution = Institution(name="Test Institution")
        db.session.add(institution)
        db.session.flush()

        admin = User(
            userid="ADMIN001",
            email="admin@example.com",
            institution_id=institution.id,
            first_name="Test",
            last_name="Admin",
            role="admin",
            status="active",
            password=generate_password_hash("AdminPassword123!"),
        )
        db.session.add(admin)
        db.session.commit()

    client = app.test_client()

    with client:
        with client.session_transaction() as session:
            session["_user_id"] = "ADMIN001"
            session["_fresh"] = True

        response = client.post(
            "/admin/educators/create",
            data={
                "userid": "TEACHER002",
                "first_name": "New",
                "last_name": "Educator",
                "email": "new@example.com",
                "institution_id": "999999",
                "password": "EducatorPassword123!",
                "confirm_password": "EducatorPassword123!",
            },
        )

    assert response.status_code == 302

    with app.app_context():
        assert User.query.filter_by(userid="TEACHER002").first() is None

def test_educator_cannot_create_educator_account():
    app = create_app({
        "TESTING": True,
        "SECRET_KEY": "test-secret-key",
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
    })

    with app.app_context():
        institution = Institution(name="Test Institution")
        db.session.add(institution)
        db.session.flush()

        educator = User(
            userid="TEACHER001",
            email="teacher@example.com",
            institution_id=institution.id,
            first_name="Test",
            last_name="Educator",
            role="educator",
            status="active",
            password=generate_password_hash("TeacherPassword123!"),
        )
        db.session.add(educator)
        db.session.commit()
        institution_id = institution.id

    client = app.test_client()

    with client:
        with client.session_transaction() as session:
            session["_user_id"] = "TEACHER001"
            session["_fresh"] = True

        response = client.post(
            "/admin/educators/create",
            data={
                "userid": "TEACHER002",
                "first_name": "New",
                "last_name": "Educator",
                "email": "new@example.com",
                "institution_id": str(institution_id),
                "password": "EducatorPassword123!",
                "confirm_password": "EducatorPassword123!",
            },
        )

    assert response.status_code == 403

    with app.app_context():
        assert User.query.filter_by(userid="TEACHER002").first() is None

def create_status_test_app():
    app = create_app({
        "TESTING": True,
        "SECRET_KEY": "test-secret-key",
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
    })

    with app.app_context():
        institution = Institution(name="Status Test Institution")
        db.session.add(institution)
        db.session.flush()

        admin = User(
            userid="STATUSADMIN",
            email="statusadmin@example.com",
            institution_id=institution.id,
            first_name="Status",
            last_name="Admin",
            role="admin",
            status="active",
            password=generate_password_hash("AdminPassword123!"),
        )

        educator = User(
            userid="STATUSTEACHER",
            email="statusteacher@example.com",
            institution_id=institution.id,
            first_name="Status",
            last_name="Educator",
            role="educator",
            status="active",
            password=generate_password_hash("TeacherPassword123!"),
        )

        db.session.add_all([admin, educator])
        db.session.commit()

    return app

def login_as_status_admin(client):
    with client.session_transaction() as session:
        session["_user_id"] = "STATUSADMIN"
        session["_fresh"] = True

def test_admin_can_deactivate_educator():
    app = create_status_test_app()
    client = app.test_client()

    with client:
        login_as_status_admin(client)
        response = client.post(
            "/admin/educators/STATUSTEACHER/status",
            data={"status": "inactive"},
        )

    assert response.status_code == 302

    with app.app_context():
        educator = db.session.get(User, "STATUSTEACHER")
        assert educator.status == "inactive"

def test_admin_can_reactivate_educator():
    app = create_status_test_app()

    with app.app_context():
        educator = db.session.get(User, "STATUSTEACHER")
        educator.status = "inactive"
        db.session.commit()

    client = app.test_client()

    with client:
        login_as_status_admin(client)
        response = client.post(
            "/admin/educators/STATUSTEACHER/status",
            data={"status": "active"},
        )

    assert response.status_code == 302

    with app.app_context():
        educator = db.session.get(User, "STATUSTEACHER")
        assert educator.status == "active"

def test_invalid_educator_status_is_rejected():
    app = create_status_test_app()
    client = app.test_client()

    with client:
        login_as_status_admin(client)
        response = client.post(
            "/admin/educators/STATUSTEACHER/status",
            data={"status": "administrator"},
        )

    assert response.status_code == 302

    with app.app_context():
        educator = db.session.get(User, "STATUSTEACHER")
        assert educator.status == "active"

def test_status_route_cannot_change_admin_account():
    app = create_status_test_app()
    client = app.test_client()

    with client:
        login_as_status_admin(client)
        response = client.post(
            "/admin/educators/STATUSADMIN/status",
            data={"status": "inactive"},
        )

    assert response.status_code == 302

    with app.app_context():
        admin = db.session.get(User, "STATUSADMIN")
        assert admin.status == "active"

def test_admin_create_educator_rejects_missing_csrf_token():
    app = create_app({
        "TESTING": True,
        "SECRET_KEY": "test-secret-key",
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": True,
    })

    with app.app_context():
        institution = Institution(name="CSRF Test Institution")
        db.session.add(institution)
        db.session.flush()

        institution_id = institution.id

        admin = User(
            userid="CSRFADMIN",
            email="csrfadmin@example.com",
            institution_id=institution_id,
            first_name="Test",
            last_name="Admin",
            role="admin",
            status="active",
            password=generate_password_hash("AdminPassword123!"),
        )
        db.session.add(admin)
        db.session.commit()

    client = app.test_client()

    # Simulate an authenticated administrator session.
    with client.session_transaction() as session:
        session["_user_id"] = "CSRFADMIN"
        session["_fresh"] = True

    # Submit without a CSRF token; the request should be rejected.
    response = client.post(
        "/admin/educators/create",
        data={
            "userid": "CSRFTEACHER",
            "first_name": "New",
            "last_name": "Educator",
            "email": "new.csrf@example.com",
            "institution_id": str(institution_id),
            "password": "EducatorPassword123!",
            "confirm_password": "EducatorPassword123!",
        },
    )

    assert response.status_code == 400

    with app.app_context():
        assert db.session.get(User, "CSRFTEACHER") is None

def test_admin_create_educator_rejects_invalid_csrf_token():
    app = create_app({
        "TESTING": True,
        "SECRET_KEY": "test-secret-key",
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": True,
    })

    client = app.test_client()

    response = client.post(
        "/admin/educators/create",
        data={"csrf_token": "invalid-token"},
    )

    assert response.status_code == 400

def test_status_change_rejects_missing_csrf_token():
    app = create_status_test_app()
    app.config["WTF_CSRF_ENABLED"] = True
    client = app.test_client()

    with client.session_transaction() as session:
        session["_user_id"] = "STATUSADMIN"
        session["_fresh"] = True

    response = client.post(
        "/admin/educators/STATUSTEACHER/status",
        data={"status": "inactive"},
    )

    assert response.status_code == 400

    with app.app_context():
        educator = db.session.get(User, "STATUSTEACHER")
        assert educator.status == "active"

def test_status_change_rejects_invalid_csrf_token():
    app = create_status_test_app()
    app.config["WTF_CSRF_ENABLED"] = True
    client = app.test_client()

    with client.session_transaction() as session:
        session["_user_id"] = "STATUSADMIN"
        session["_fresh"] = True

    response = client.post(
        "/admin/educators/STATUSTEACHER/status",
        data={
            "status": "inactive",
            "csrf_token": "invalid-token",
        },
    )

    assert response.status_code == 400

    with app.app_context():
        educator = db.session.get(User, "STATUSTEACHER")
        assert educator.status == "active"

def test_deactivated_educator_loses_access_with_existing_session():
    app = create_status_test_app()
    client = app.test_client()

    # Log in the educator while the account is active.
    with client.session_transaction() as session:
        session["_user_id"] = "STATUSTEACHER"
        session["_fresh"] = True

    # Confirm the existing session can access the protected home page.
    response = client.get("/")
    assert response.status_code == 200

    # An administrator deactivates the educator's account.
    with app.app_context():
        educator = db.session.get(User, "STATUSTEACHER")
        educator.status = "inactive"
        db.session.commit()

    # The same client/session must now lose access.
    response = client.get("/")

    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]

def test_unauthenticated_user_cannot_create_educator():
    app = create_status_test_app()
    client = app.test_client()

    response = client.post(
        "/admin/educators/create",
        data={
            "userid": "UNAUTH_TEACHER",
            "first_name": "Test",
            "last_name": "Educator",
            "email": "unauth@example.com",
            "institution_id": "1",
            "password": "TestPassword123!",
            "confirm_password": "TestPassword123!",
        },
    )

    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]

    with app.app_context():
        assert db.session.get(User, "UNAUTH_TEACHER") is None

def test_unauthenticated_user_cannot_change_educator_status():
    app = create_status_test_app()
    client = app.test_client()

    response = client.post(
        "/admin/educators/STATUSTEACHER/status",
        data={"status": "inactive"},
    )

    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]

    with app.app_context():
        educator = db.session.get(User, "STATUSTEACHER")
        assert educator.status == "active"

def test_create_educator_logs_database_error_and_shows_generic_message(caplog):
    from unittest.mock import patch
    import logging

    app = create_status_test_app()
    client = app.test_client()
    login_as_status_admin(client)

    with caplog.at_level(logging.ERROR, logger="app.admin.routes"):
        with patch(
            "app.admin.routes.db.session.commit",
            side_effect=RuntimeError("Sensitive internal database detail"),
        ):
            response = client.post(
                "/admin/educators/create",
                data={
                    "userid": "LOGTESTTEACHER",
                    "first_name": "Log",
                    "last_name": "Test",
                    "email": "logtest@example.com",
                    "institution_id": "1",
                    "password": "TestPassword123!",
                    "confirm_password": "TestPassword123!",
                },
                follow_redirects=True,
            )

    assert "Failed to create educator account." in caplog.text
    assert "Sensitive internal database detail" in caplog.text
    assert "Sensitive internal database detail" not in response.get_data(
        as_text=True
    )
    assert "Could not create the educator account. Please try again." in (
        response.get_data(as_text=True)
    )
