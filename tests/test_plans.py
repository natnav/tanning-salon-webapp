from datetime import datetime

from tests.helpers import auth_headers, login_user, register_user


def test_purchase_five_pack_sets_credits_and_expiry(client):
    register_user(client, email="pack@example.com")
    token = login_user(client, email="pack@example.com")

    plans_response = client.get("/plans")
    assert plans_response.status_code == 200
    five_pack = next(plan for plan in plans_response.json() if plan["name"] == "5-Pack")

    response = client.post(f"/plans/purchase/{five_pack['id']}", headers=auth_headers(token))
    assert response.status_code == 201

    data = response.json()
    assert data["remaining_credits"] == 5
    assert data["visits_used"] == 0
    start_date = datetime.fromisoformat(data["start_date"])
    expiry_date = datetime.fromisoformat(data["expiry_date"])
    assert (expiry_date - start_date).days == 90


def test_purchase_monthly_plan_sets_cap_and_expiry(client):
    register_user(client, email="monthly@example.com")
    token = login_user(client, email="monthly@example.com")

    plans_response = client.get("/plans")
    monthly_plan = next(plan for plan in plans_response.json() if plan["type"] == "MONTHLY")

    response = client.post(f"/plans/purchase/{monthly_plan['id']}", headers=auth_headers(token))
    assert response.status_code == 201

    data = response.json()
    assert data["remaining_credits"] is None
    assert data["visits_used"] == 0
    start_date = datetime.fromisoformat(data["start_date"])
    expiry_date = datetime.fromisoformat(data["expiry_date"])
    assert (expiry_date - start_date).days == 30
