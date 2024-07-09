import unittest
from django.urls import reverse
from rest_framework.test import APIClient
from users.models import User
from django.test import TestCase


class TokenGenerationTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="testuser@example.com",
            firstName="Test",
            lastName="User",
            password="password123",
        )
        self.login_url = reverse("login")

    def test_token_user_details(self):
        response = self.client.post(
            self.login_url, {"email": self.user.email, "password": "password123"}
        )
        self.assertEqual(response.status_code, 200)
        access_token = response.data["data"]["accessToken"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        user_id = response.data["data"]["user"]["userId"]
        self.assertEqual(
            user_id, str(self.user.userId)
        )  # Ensuring comparison is between strings
