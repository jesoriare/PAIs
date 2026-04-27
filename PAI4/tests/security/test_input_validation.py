from __future__ import annotations


def test_feedback_rejects_overlong_input(client, login_member):
    login_member()
    response = client.post("/feedback", data={"message": "A" * 201})

    assert response.status_code == 400

    feedback_page = client.get("/feedback")
    assert b"data-comment-id=" not in feedback_page.data


def test_checkout_rejects_invalid_quantities(client, login_member):
    login_member()
    response = client.post(
        "/checkout",
        json={"items": [{"sku": "SKU-BOOK", "quantity": 0}], "client_total": "0.01"},
    )

    assert response.status_code == 400
