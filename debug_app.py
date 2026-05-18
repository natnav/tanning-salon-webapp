from fastapi.testclient import TestClient
from app.main import app
import sys

def debug_app():
    print(f"Python path: {sys.path}")
    print(f"App routes: {[route.path for route in app.routes]}")
    client = TestClient(app)
    response = client.get("/")
    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.json() if response.status_code == 200 else response.text}")
    
    response = client.post("/auth/register", json={"email": "test@example.com", "password": "password123", "full_name": "Test User"})
    print(f"Register status: {response.status_code}")
    print(f"Register body: {response.json() if response.status_code == 201 else response.text}")

if __name__ == "__main__":
    debug_app()
