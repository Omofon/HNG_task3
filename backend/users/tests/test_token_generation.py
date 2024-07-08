import unittest
from rest_framework_simplejwt.tokens import RefreshToken
from django.test import TestCase
from users.models import User


class TokenGenerationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@example.com",
            firstName="Test",
            lastName="User",
            password="password123",
        )

    def test_token_expiry(self):
        refresh = RefreshToken.for_user(self.user)
        access_token = refresh.access_token
        self.assertTrue(access_token)

    def test_token_user_details(self):
        refresh = RefreshToken.for_user(self.user)
        access_token = refresh.access_token
        user_id = access_token.payload["user_id"]
        self.assertEqual(user_id, str(self.user.userId))


if __name__ == "__main__":
    unittest.main()
