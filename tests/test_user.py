import pytest
from fastapi.testclient import TestClient
from app import app


client = TestClient(app)
CLIENT_JWT = None

@pytest.fixture(scope="function", autouse=True)
async def load_prediction_model():
    async with app.lifespan_context():
        yield

def get_test_user_and_token():
    response = client.post(
        "/login",
        json={"login": "test_user", "password": "test_password"}
    )

    global CLIENT_JWT
    CLIENT_JWT = response.json()["access_token"]

def test_make_prediction():
    get_test_user_and_token()
    response = client.post(
        "/predict",
        json={"input_text": "test_text", "min_len": 5, "max_len": 20},
        headers={"Authorization": f"Bearer {CLIENT_JWT}"}
    )

    assert response.status_code == 200
    assert response.json()

def test_get_user():
    global CLIENT_JWT
    response = client.get(
        "/get_user",
        headers={"Authorization": f"Bearer {CLIENT_JWT}"}
    )

    assert response.status_code == 200
    assert response.json()

def test_balance_increse():
    global CLIENT_JWT
    response = client.get(
        "/balance/increase?amount=5",
        headers={"Authorization": f"Bearer {CLIENT_JWT}"}
    )

    assert response.status_code == 200
    assert response.json()

def test_history():
    global CLIENT_JWT
    response = client.get(
        "/history",
        headers={"Authorization": f"Bearer {CLIENT_JWT}"}
    )

    assert response.status_code == 200
