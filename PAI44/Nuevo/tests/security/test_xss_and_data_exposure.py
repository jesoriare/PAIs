from __future__ import annotations


def test_feedback_output_is_escaped(client, login_member):
    login_member()
    response = client.post(
        "/feedback",
        data={"message": "<script>alert(1)</script>"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"<script>alert(1)</script>" not in response.data
    assert b"&lt;script&gt;alert(1)&lt;/script&gt;" in response.data


def test_profile_omits_password_material(client, login_member):
    login_member()
    response = client.get("/profile")
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["username"] == "member"
    assert payload["role"] == "member"
    assert "password_hash" not in payload
