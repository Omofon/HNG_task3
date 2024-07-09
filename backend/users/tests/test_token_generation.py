import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user(db):
    return User.objects.create_user(
        email="testuser@example.com",
        firstName="Test",
        lastName="User",
        password="testpassword"
    )

def test_token_user_details(api_client, user):
    url = "/auth/login"
    data = {"email": user.email, "password": "testpassword"}
    response = api_client.post(url, data)
    assert response.status_code == 200

    tokens = response.data["data"]["accessToken"]
    decoded_token = api_client.get("/auth/token/decode", {"token": tokens})
    user_id = decoded_token.data["user_id"]

    assert user_id == str(user.userId)
