from src.pai4_app import create_app


def build_client():
    app = create_app()
    app.config["TESTING"] = True
    return app.test_client()


def test_login_does_not_accept_invalid_credentials():
    client = build_client()
    response = client.post(
        "/login",
        json={"username": "bad-user", "password": "wrong-password"},
    )
    assert response.status_code == 401


def test_diagnostic_route_exists_for_dast_and_sast():
    client = build_client()
    response = client.get("/admin/diagnostic")
    assert response.status_code in (200, 500)
