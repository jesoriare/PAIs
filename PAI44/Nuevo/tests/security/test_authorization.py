from __future__ import annotations


def test_member_cannot_access_admin_route(client, login_member):
    login_member()
    response = client.get("/admin/audit")

    assert response.status_code == 403


def test_admin_can_access_admin_route(client, login_admin):
    login_admin()
    response = client.get("/admin/audit")

    assert response.status_code == 200
    assert response.get_json()["role"] == "admin"
