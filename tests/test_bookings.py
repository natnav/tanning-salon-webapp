from datetime import UTC, datetime, timedelta

from app.models.user_plan import UserPlan
from tests.helpers import auth_headers, login_user, register_user


def test_create_booking_with_sufficient_credits(client, db_session):
    register_user(client, email="booking@example.com")
    token = login_user(client, email="booking@example.com")

    plans = client.get("/plans").json()
    five_pack = next(plan for plan in plans if plan["name"] == "5-Pack")
    services = client.get("/services").json()
    uv_tanning = next(service for service in services if service["name"] == "UV Tanning")

    purchase_response = client.post(f"/plans/purchase/{five_pack['id']}", headers=auth_headers(token))
    assert purchase_response.status_code == 201

    start_time = (datetime.now(UTC) + timedelta(days=1)).isoformat()
    booking_response = client.post(
        "/bookings",
        headers=auth_headers(token),
        json={"service_id": uv_tanning["id"], "start_time": start_time},
    )
    assert booking_response.status_code == 201

    my_bookings_response = client.get("/bookings/me", headers=auth_headers(token))
    assert my_bookings_response.status_code == 200
    assert len(my_bookings_response.json()) == 1

    purchase = purchase_response.json()
    updated_user_plan = db_session.get(UserPlan, purchase["id"])
    assert updated_user_plan is not None
    assert updated_user_plan.remaining_credits == 4


def test_booking_exceeding_room_capacity_fails(client):
    register_user(client, email="one@example.com")
    token_one = login_user(client, email="one@example.com")
    register_user(client, email="two@example.com")
    token_two = login_user(client, email="two@example.com")
    register_user(client, email="three@example.com")
    token_three = login_user(client, email="three@example.com")

    plans = client.get("/plans").json()
    five_pack = next(plan for plan in plans if plan["name"] == "5-Pack")
    services = client.get("/services").json()
    uv_tanning = next(service for service in services if service["name"] == "UV Tanning")

    for token in (token_one, token_two, token_three):
        purchase_response = client.post(f"/plans/purchase/{five_pack['id']}", headers=auth_headers(token))
        assert purchase_response.status_code == 201

    start_time = (datetime.now(UTC) + timedelta(days=2)).replace(microsecond=0).isoformat()
    first = client.post(
        "/bookings",
        headers=auth_headers(token_one),
        json={"service_id": uv_tanning["id"], "start_time": start_time},
    )
    second = client.post(
        "/bookings",
        headers=auth_headers(token_two),
        json={"service_id": uv_tanning["id"], "start_time": start_time},
    )
    third = client.post(
        "/bookings",
        headers=auth_headers(token_three),
        json={"service_id": uv_tanning["id"], "start_time": start_time},
    )

    assert first.status_code == 201
    assert second.status_code == 201
    assert third.status_code == 400
    assert third.json()["detail"] == "No room capacity available"
