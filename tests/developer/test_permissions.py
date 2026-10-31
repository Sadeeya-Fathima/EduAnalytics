from .conftest import login_as_developer, protected_test_app


def test_enabled_developer_tools_allow_loopback_developer():
    app = protected_test_app(
        EDUANALYTICS_ENV="development",
        EDUANALYTICS_DEV_TOOLS_ENABLED=True,
    )
    client = app.test_client()
    login_as_developer(client)

    response = client.get("/developer", environ_base={"REMOTE_ADDR": "127.0.0.1"})

    assert response.status_code == 200


def test_local_only_developer_tools_reject_lan_request():
    app = protected_test_app(
        EDUANALYTICS_ENV="development",
        EDUANALYTICS_DEV_TOOLS_ENABLED=True,
    )
    client = app.test_client()
    login_as_developer(client)

    response = client.get("/developer", environ_base={"REMOTE_ADDR": "192.168.1.20"})

    assert response.status_code == 403


def test_developer_tools_do_not_trust_forwarded_headers():
    app = protected_test_app(
        EDUANALYTICS_ENV="development",
        EDUANALYTICS_DEV_TOOLS_ENABLED=True,
    )
    client = app.test_client()
    login_as_developer(client)

    response = client.get(
        "/developer",
        environ_base={
            "REMOTE_ADDR": "192.168.1.20",
            "HTTP_X_FORWARDED_FOR": "127.0.0.1",
        },
    )

    assert response.status_code == 403


def test_non_developer_is_denied_when_tools_are_enabled():
    app = protected_test_app(
        role="educator",
        EDUANALYTICS_ENV="development",
        EDUANALYTICS_DEV_TOOLS_ENABLED=True,
    )
    client = app.test_client()
    login_as_developer(client, user_id="educator001")

    response = client.get("/developer")

    assert response.status_code == 403
