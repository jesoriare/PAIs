from __future__ import annotations

from urllib.parse import parse_qs, urlparse


def test_dashboard_requires_login(client):
    response = client.get("/dashboard", follow_redirects=False)
    redirect_target = urlparse(response.headers["Location"])

    assert response.status_code == 302
    assert redirect_target.path == "/login"
    assert parse_qs(redirect_target.query)["next"] == ["/dashboard"]


def test_successful_login_sets_session_and_redirects_to_dashboard(client, login_member):
    response = login_member()

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/dashboard")

    with client.session_transaction() as session_state:
        assert isinstance(session_state.get("user_id"), int)
