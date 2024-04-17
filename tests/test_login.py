from fastapi.testclient import TestClient
from app import app


client = TestClient(app)

def test_register_user():
    response = client.post(
        "/register/",
        json={"login": "test_user", "password": "test_password"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_login_user():
    response = client.post(
        "/login/",
        json={"login": "test_user", "password": "test_password"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"
