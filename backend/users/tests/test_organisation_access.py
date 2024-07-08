import unittest
from django.urls import reverse
from rest_framework.test import APIClient
from django.test import TestCase
from users.models import User, Organisation


class OrganisationAccessTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(
            email="user1@example.com",
            firstName="User",
            lastName="One",
            password="password123",
        )
        self.user2 = User.objects.create_user(
            email="user2@example.com",
            firstName="User",
            lastName="Two",
            password="password123",
        )
        self.org1 = Organisation.objects.create(name="Org1")
        self.org1.users.add(self.user1)

    def test_user_cannot_see_other_organisation_data(self):
        self.client.force_authenticate(user=self.user2)  # Authenticate user2
        url = reverse("organisation-detail", args=[self.org1.orgId])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)


if __name__ == "__main__":
    unittest.main()
