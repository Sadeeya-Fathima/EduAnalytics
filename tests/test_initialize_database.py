import pytest

from app import create_app
from app.extensions import db
from app.models import Institution, User
from scripts import initialize_database


def test_initializer_stops_when_admin_exists(monkeypatch, capsys):
    app = create_app({
        "TESTING": True,
        "SECRET_KEY": "test-secret-key",
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })

    with app.app_context():
        db.create_all()

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
            password="test-password-hash",
        )
        db.session.add(admin)
        db.session.commit()

    monkeypatch.setattr(initialize_database, "create_app", lambda: app)

    def unexpected_input(*args, **kwargs):
        raise AssertionError("Initializer should stop before requesting input")

    monkeypatch.setattr("builtins.input", unexpected_input)

    initialize_database.main()

    output = capsys.readouterr().out
    assert "an Admin account exists" in output
    assert "No changes were made to the database." in output

    with app.app_context():
        assert Institution.query.count() == 1
        assert User.query.filter_by(role="admin").count() == 1
        db.session.remove()
        db.drop_all()

def test_initializer_prompts_when_no_admin_exists(monkeypatch, capsys):
    app = create_app({
        "TESTING": True,
        "SECRET_KEY": "test-secret-key",
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })

    monkeypatch.setattr(initialize_database, "create_app", lambda: app)

    def stop_at_first_prompt(prompt):
        assert prompt == "Institution name: "
        raise RuntimeError("Stopped safely at first prompt")

    monkeypatch.setattr("builtins.input", stop_at_first_prompt)

    with pytest.raises(
        RuntimeError,
        match="Stopped safely at first prompt",
    ):
        initialize_database.main()

    output = capsys.readouterr().out
    assert "EduAnalytics - Initial Database Setup" in output
    assert "Initial setup is already complete" not in output


def test_initializer_creates_initial_admin_in_fresh_database(
    monkeypatch, capsys
):
    app = create_app({
        "TESTING": True,
        "SECRET_KEY": "test-secret-key",
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })

    monkeypatch.setattr(initialize_database, "create_app", lambda: app)

    answers = iter([
        "Test Institution",
        "ADMIN002",
        "admin2@example.com",
        "Taylor",
        "Admin",
    ])
    passwords = iter(["secure-test-password", "secure-test-password"])

    monkeypatch.setattr("builtins.input", lambda prompt="": next(answers))
    monkeypatch.setattr(
        initialize_database,
        "getpass",
        lambda prompt="": next(passwords),
    )

    initialize_database.main()

    output = capsys.readouterr().out
    assert "Setup completed successfully." in output

    with app.app_context():
        institution = Institution.query.filter_by(
            name="Test Institution"
        ).first()
        admin = User.query.filter_by(userid="ADMIN002").first()

        assert institution is not None
        assert admin is not None
        assert admin.email == "admin2@example.com"
        assert admin.role == "admin"
        assert admin.institution_id == institution.id
        assert admin.password != "secure-test-password"


def test_initializer_stops_when_non_admin_user_exists(
    monkeypatch, capsys
):
    app = create_app({
        "TESTING": True,
        "SECRET_KEY": "test-secret-key",
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })

    with app.app_context():
        institution = Institution(name="Existing Institution")
        db.session.add(institution)
        db.session.flush()

        user = User(
            userid="USER001",
            email="user@example.com",
            institution_id=institution.id,
            first_name="Existing",
            last_name="User",
            role="educator",
            status="active",
            password="test-password-hash",
        )
        db.session.add(user)
        db.session.commit()

    monkeypatch.setattr(initialize_database, "create_app", lambda: app)

    def unexpected_input(*args, **kwargs):
        raise AssertionError(
            "Initializer must stop when a user already exists"
        )

    monkeypatch.setattr("builtins.input", unexpected_input)

    initialize_database.main()

    output = capsys.readouterr().out
    assert "No changes were made to the database." in output

    with app.app_context():
        assert Institution.query.count() == 1
        assert User.query.count() == 1
