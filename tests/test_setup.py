
from werkzeug.security import check_password_hash

from app import create_app
from app.extensions import db
from app.models import Institution, User

from concurrent.futures import ThreadPoolExecutor
from threading import Barrier


def make_app():
    return create_app({
        "TESTING": True,
        "SECRET_KEY": "test-secret-key",
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
    })


def test_setup_page_loads_on_localhost():
    app = make_app()
    client = app.test_client()

    response = client.get("/setup/", environ_base={"REMOTE_ADDR": "127.0.0.1"})

    assert response.status_code == 200
    assert b"Welcome to EduAnalytics" in response.data


def test_setup_blocks_non_local_request():
    app = make_app()
    client = app.test_client()

    response = client.get("/setup/", environ_base={"REMOTE_ADDR": "192.168.1.20"})

    assert response.status_code == 403


def test_setup_stops_when_admin_exists():
    app = make_app()

    with app.app_context():
        db.create_all()
        institution = Institution(name="Existing Institution")
        db.session.add(institution)
        db.session.flush()

        db.session.add(User(
            userid="ADMIN001",
            email="admin@example.com",
            institution_id=institution.id,
            first_name="Existing",
            last_name="Admin",
            role="admin",
            status="active",
            password="unused-test-hash",
        ))
        db.session.commit()

    client = app.test_client()
    response = client.get("/setup/", environ_base={"REMOTE_ADDR": "127.0.0.1"})

    assert response.status_code == 403
    assert b"already set up" in response.data.lower()


def test_setup_creates_initial_admin():
    app = make_app()
    client = app.test_client()

    response = client.post(
        "/setup/",
        environ_base={"REMOTE_ADDR": "127.0.0.1"},
        data={
            "institution_name": "New Institution",
            "userid": "ADMIN002",
            "email": "newadmin@example.com",
            "first_name": "New",
            "last_name": "Admin",
            "password": "StrongPassword123!",
            "confirm_password": "StrongPassword123!",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/auth/login")

    with app.app_context():
        institution = Institution.query.filter_by(
            name="New Institution"
        ).one()
        admin = User.query.filter_by(userid="ADMIN002").one()

        assert admin.role == "admin"
        assert admin.institution_id == institution.id
        assert check_password_hash(admin.password, "StrongPassword123!")
        assert admin.password != "StrongPassword123!"


def test_setup_rejects_short_password_without_creating_records():
    app = make_app()
    client = app.test_client()

    response = client.post(
        "/setup/",
        environ_base={"REMOTE_ADDR": "127.0.0.1"},
        data={
            "institution_name": "Invalid Institution",
            "userid": "ADMIN003",
            "email": "short@example.com",
            "first_name": "Test",
            "last_name": "Admin",
            "password": "short",
            "confirm_password": "short",
        },
    )

    assert response.status_code == 400

    with app.app_context():
        assert Institution.query.count() == 0
        assert User.query.count() == 0


def test_setup_rejects_mismatched_passwords_without_creating_records():
    app = make_app()
    client = app.test_client()

    response = client.post(
        "/setup/",
        environ_base={"REMOTE_ADDR": "127.0.0.1"},
        data={
            "institution_name": "Invalid Institution",
            "userid": "ADMIN004",
            "email": "mismatch@example.com",
            "first_name": "Test",
            "last_name": "Admin",
            "password": "StrongPassword123!",
            "confirm_password": "DifferentPassword123!",
        },
    )

    assert response.status_code == 400

    with app.app_context():
        assert Institution.query.count() == 0
        assert User.query.count() == 0


def test_setup_stops_when_non_admin_user_exists():
    app = make_app()

    with app.app_context():
        db.create_all()
        institution = Institution(name="Partially Set Up Institution")
        db.session.add(institution)
        db.session.flush()

        db.session.add(User(
            userid="TEACHER001",
            email="teacher@example.com",
            institution_id=institution.id,
            first_name="Test",
            last_name="Teacher",
            role="educator",
            status="active",
            password="unused-test-hash",
        ))
        db.session.commit()

    client = app.test_client()
    response = client.get(
        "/setup/",
        environ_base={"REMOTE_ADDR": "127.0.0.1"},
    )

    assert response.status_code == 403
    assert b"already set up" in response.data.lower()

    with app.app_context():
        assert Institution.query.count() == 1
        assert User.query.count() == 1
        assert User.query.filter_by(role="admin").count() == 0


def test_setup_rejects_repeat_submission_without_changing_records():
    app = make_app()
    client = app.test_client()

    form_data = {
        "institution_name": "Test Institution",
        "userid": "ADMIN005",
        "email": "admin5@example.com",
        "first_name": "Test",
        "last_name": "Admin",
        "password": "StrongPassword123!",
        "confirm_password": "StrongPassword123!",
    }

    first_response = client.post(
        "/setup/",
        environ_base={"REMOTE_ADDR": "127.0.0.1"},
        data=form_data,
    )
    assert first_response.status_code == 302

    with app.app_context():
        initial_institutions = Institution.query.count()
        initial_users = User.query.count()

    second_response = client.post(
        "/setup/",
        environ_base={"REMOTE_ADDR": "127.0.0.1"},
        data=form_data,
    )

    assert second_response.status_code == 403

    with app.app_context():
        assert Institution.query.count() == initial_institutions
        assert User.query.count() == initial_users
        assert User.query.filter_by(userid="ADMIN005").count() == 1


from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

def test_concurrent_setup_requests_create_only_one_admin():
    app = make_app()
    barrier = Barrier(2)

    form_data = {
        "institution_name": "Concurrent Test Institution",
        "userid": "CONCURRENT_ADMIN",
        "email": "concurrent@example.com",
        "first_name": "Concurrent",
        "last_name": "Admin",
        "password": "StrongPassword123!",
        "confirm_password": "StrongPassword123!",
    }

    def submit_setup():
        with app.test_client() as client:
            barrier.wait(timeout=5)
            return client.post(
                "/setup/",
                environ_base={"REMOTE_ADDR": "127.0.0.1"},
                data=form_data,
            ).status_code

    with ThreadPoolExecutor(max_workers=2) as executor:
        statuses = list(executor.map(lambda _: submit_setup(), range(2)))

    assert sorted(statuses) == [302, 403]

    with app.app_context():
        assert Institution.query.count() == 1
        assert User.query.filter_by(userid="CONCURRENT_ADMIN").count() == 1
        assert User.query.filter_by(role="admin").count() == 1
