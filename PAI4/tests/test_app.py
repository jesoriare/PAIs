from src.pai4_app import create_app


def build_client():
    app = create_app()
    app.config["TESTING"] = True
    return app.test_client()


def test_home_endpoint():
    client = build_client()
    response = client.get("/")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_health_endpoint():
    client = build_client()
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "healthy"


def test_products_endpoint():
    client = build_client()
    response = client.get("/products")
    body = response.get_json()
    assert response.status_code == 200
    assert body["count"] == 3


def test_login_rejects_empty_payload():
    client = build_client()
    response = client.post("/login", json={})
    assert response.status_code == 400


def test_login_accepts_demo_credentials():
    client = build_client()
    response = client.post(
        "/login",
        json={"username": "security-team", "password": "ChangeMe123!"},
    )
    assert response.status_code == 200
    assert response.get_json()["token"] == "demo-token"
