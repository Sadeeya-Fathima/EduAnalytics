from app.auth.decorators import developer_tools_enabled

from .conftest import login_as_developer, protected_test_app


def test_developer_tools_are_disabled_by_default():
    app = protected_test_app()
    assert developer_tools_enabled.__name__ == "developer_tools_enabled"
    client = app.test_client()
    login_as_developer(client)

    response = client.get("/developer")

    assert response.status_code == 403


def test_developer_tools_require_explicit_development_configuration():
    app = protected_test_app(
        EDUANALYTICS_ENV="production",
        EDUANALYTICS_DEV_TOOLS_ENABLED=True,
    )
    client = app.test_client()
    login_as_developer(client)

    response = client.get("/developer")

    assert response.status_code == 403


def test_developer_tools_require_enablement_flag():
    app = protected_test_app(
        EDUANALYTICS_ENV="development",
        EDUANALYTICS_DEV_TOOLS_ENABLED=False,
    )
    client = app.test_client()
    login_as_developer(client)

    response = client.get("/developer")

    assert response.status_code == 403
