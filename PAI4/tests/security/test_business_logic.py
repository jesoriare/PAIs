from __future__ import annotations


def test_checkout_total_is_calculated_server_side(client, login_member):
    login_member()
    response = client.post(
        "/checkout",
        json={
            "items": [
                {"sku": "SKU-BOOK", "quantity": 1},
                {"sku": "SKU-LAB", "quantity": 1},
            ],
            "client_total": "0.01",
        },
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["server_total"] == "45.00"
    assert payload["submitted_total"] == "0.01"
    assert payload["client_total_accepted"] is False
