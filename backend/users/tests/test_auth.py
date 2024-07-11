import unittest
from rest_framework.test import APIClient
from django.urls import reverse
from users.models import User, Organisation


class AuthRegisterTestCase(unittest.TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse("register")
        self.login_url = reverse("login")
        self.valid_user_data = {
            "firstName": "John",
            "lastName": "Doe",
            "email": "johndoe@example.com",
            "password": "password123",
            "phone": "1234567890",
        }

    def test_register_user_successfully_with_default_organisation(self):
        response = self.client.post(
            self.register_url, self.valid_user_data, format="json"
        )
        self.assertEqual(response.status_code, 201)
        self.assertIn("accessToken", response.data["data"])
        self.assertIn("user", response.data["data"])
        self.assertEqual(response.data["data"]["user"]["firstName"], "John")
        self.assertEqual(response.data["data"]["user"]["lastName"], "Doe")

        # Verify the default organisation name
        user = User.objects.get(email=self.valid_user_data["email"])
        self.assertTrue(
            Organisation.objects.filter(name="John's Organisation", users=user).exists()
        )

    def test_login_user_successfully(self):
        self.client.post(self.register_url, self.valid_user_data, format="json")
        login_data = {"email": "johndoe@example.com", "password": "password123"}
        response = self.client.post(self.login_url, login_data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertIn("accessToken", response.data["data"])
        self.assertIn("user", response.data["data"])

    def test_fail_if_required_fields_are_missing(self):
        required_fields = ["firstName", "lastName", "email", "password"]
        for field in required_fields:
            data = self.valid_user_data.copy()
            data.pop(field)
            response = self.client.post(self.register_url, data, format="json")
            self.assertEqual(response.status_code, 422)
            self.assertIn("errors", response.data)

    def test_fail_if_duplicate_email_or_userid(self):
        self.client.post(self.register_url, self.valid_user_data, format="json")
        response = self.client.post(
            self.register_url, self.valid_user_data, format="json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("status", response.data)
        self.assertEqual(response.data["status"], "Bad request")


if __name__ == "__main__":
    unittest.main()
