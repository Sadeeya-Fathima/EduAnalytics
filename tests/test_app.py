
from app import create_app


def test_home_page_requires_login():
    app = create_app({
        "TESTING": True,
        "SECRET_KEY": "test-secret-key",
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
    })

    client = app.test_client()
    response = client.get("/")

    assert response.status_code == 302
    assert response.headers["Location"].startswith("/auth/login?")
    assert "next=%2F" in response.headers["Location"]
