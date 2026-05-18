from fastapi.testclient import TestClient


def register_user(
    client: TestClient,
    *,
    email: str,
    password: str = "password123",
    full_name: str = "Test User",
) -> dict:
    response = client.post(
        "/auth/register",
        json={"email": email, "password": password, "full_name": full_name},
    )
    assert response.status_code == 201, response.text
    return response.json()


def login_user(
    client: TestClient,
    *,
    email: str,
    password: str = "password123",
) -> str:
    response = client.post("/auth/token", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}
