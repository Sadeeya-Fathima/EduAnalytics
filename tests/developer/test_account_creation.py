from werkzeug.security import check_password_hash

from app.extensions import db
from app.models import Institution, User
from scripts import create_dev_account


def configured_app(create_app):
    app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-secret-key",
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "EDUANALYTICS_ENV": "development",
            "EDUANALYTICS_DEV_TOOLS_ENABLED": True,
        }
    )
    with app.app_context():
        db.session.add(Institution(name="Test Institution"))
        db.session.commit()
    return app


def test_valid_local_provisioning_creates_developer(monkeypatch, capsys):
    from app import create_app

    app = configured_app(create_app)
    monkeypatch.setattr(create_dev_account, "create_app", lambda: app)
    answers = iter(["developer01", "developer@example.com", "Dev", "User"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(answers))
    passwords = iter(["secure-password", "secure-password"])
    monkeypatch.setattr(create_dev_account, "getpass", lambda prompt="": next(passwords))

    result = create_dev_account.main()

    assert result == 0
    assert "created successfully" in capsys.readouterr().out
    with app.app_context():
        user = User.query.filter_by(userid="developer01").one()
        assert user.role == "developer"
        assert user.email == "developer@example.com"
        assert user.first_name == "Dev"
        assert user.last_name == "User"
        assert check_password_hash(user.password, "secure-password")


def test_provisioning_rejects_disabled_tools(monkeypatch, capsys):
    from app import create_app

    app = configured_app(create_app)
    app.config["EDUANALYTICS_DEV_TOOLS_ENABLED"] = False
    monkeypatch.setattr(create_dev_account, "create_app", lambda: app)

    assert create_dev_account.main() == 1
    assert "disabled" in capsys.readouterr().err


def test_provisioning_rejects_non_development_installation(monkeypatch, capsys):
    from app import create_app

    app = configured_app(create_app)
    app.config["EDUANALYTICS_ENV"] = "production"
    monkeypatch.setattr(create_dev_account, "create_app", lambda: app)

    assert create_dev_account.main() == 1
    assert "development" in capsys.readouterr().err


def test_duplicate_user_is_rejected_without_prompting_for_password(
    monkeypatch, capsys
):
    from app import create_app

    app = configured_app(create_app)
    with app.app_context():
        institution = Institution.query.one()
        db.session.add(
            User(
                userid="developer01",
                email="existing@example.com",
                institution_id=institution.id,
                first_name="Existing",
                last_name="Developer",
                role="developer",
                status="active",
                password="existing-hash",
            )
        )
        db.session.commit()

    monkeypatch.setattr(create_dev_account, "create_app", lambda: app)
    answers = iter(["developer01", "developer@example.com", "Dev", "User"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(answers))
    monkeypatch.setattr(
        create_dev_account,
        "getpass",
        lambda prompt="": (_ for _ in ()).throw(AssertionError("password prompt")),
    )

    assert create_dev_account.main() == 1
    assert "already exists" in capsys.readouterr().err


def test_short_password_is_rejected_without_creating_user(monkeypatch):
    from app import create_app

    app = configured_app(create_app)
    monkeypatch.setattr(create_dev_account, "create_app", lambda: app)
    answers = iter(["developer01", "new@example.com", "Dev", "User"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(answers))
    passwords = iter(["short", "short"])
    monkeypatch.setattr(create_dev_account, "getpass", lambda prompt="": next(passwords))

    assert create_dev_account.main() == 1
    with app.app_context():
        assert User.query.filter_by(userid="developer01").count() == 0


def test_mismatched_password_is_rejected_without_creating_user(monkeypatch):
    from app import create_app

    app = configured_app(create_app)
    monkeypatch.setattr(create_dev_account, "create_app", lambda: app)
    answers = iter(["developer01", "developer@example.com", "Dev", "User"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(answers))
    passwords = iter(["secure-password", "different-password"])
    monkeypatch.setattr(create_dev_account, "getpass", lambda prompt="": next(passwords))

    assert create_dev_account.main() == 1
    with app.app_context():
        assert User.query.filter_by(userid="developer01").count() == 0
