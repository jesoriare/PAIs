from __future__ import annotations

import pytest
from werkzeug.security import generate_password_hash

from app.db import init_db, upsert_user
from app.main import create_app


@pytest.fixture()
def app(tmp_path):
    db_path = tmp_path / "pai4-test.db"
    application = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-secret-key",
            "DATABASE_PATH": str(db_path),
        }
    )
    init_db(str(db_path))
    upsert_user(str(db_path), "member", generate_password_hash("MemberPass!123"), "member")
    upsert_user(str(db_path), "admin", generate_password_hash("AdminPass!123"), "admin")
    return application


@pytest.fixture()
def client(app):
    return app.test_client()


def login(client, username: str, password: str):
    return client.post(
        "/login",
        data={"username": username, "password": password},
        follow_redirects=False,
    )


@pytest.fixture()
def login_member(client):
    def _login_member():
        return login(client, "member", "MemberPass!123")

    return _login_member


@pytest.fixture()
def login_admin(client):
    def _login_admin():
        return login(client, "admin", "AdminPass!123")

    return _login_admin
