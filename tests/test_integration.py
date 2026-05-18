from datetime import UTC, datetime, timedelta

from app.models.user import User
from tests.helpers import auth_headers, login_user, register_user


def test_admin_walk_in_bypasses_client_plan_and_supports_teeth_whitening(client, db_session):
    admin = register_user(client, email="admin@example.com", full_name="Admin User")
    customer = register_user(client, email="walkin@example.com", full_name="Walk In User")

    admin_record = db_session.get(User, admin["id"])
    assert admin_record is not None
    admin_record.is_admin = True
    db_session.commit()

    admin_token = login_user(client, email="admin@example.com")
    services = client.get("/services").json()
    teeth_whitening = next(service for service in services if service["name"] == "Teeth Whitening")

    response = client.post(
        "/bookings/walk-in",
        headers=auth_headers(admin_token),
        json={
            "user_id": customer["id"],
            "service_id": teeth_whitening["id"],
            "start_time": (datetime.now(UTC) + timedelta(hours=1)).isoformat(),
        },
    )
    assert response.status_code == 201

    data = response.json()
    assert data["user_id"] == customer["id"]
    assert data["service_id"] == teeth_whitening["id"]
    assert data["is_walk_in"] is True
