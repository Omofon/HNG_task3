import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from users.models import Organisation

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

@pytest.fixture
def another_user(db):
    return User.objects.create_user(
        email="anotheruser@example.com",
        firstName="Another",
        lastName="User",
        password="anotherpassword"
    )

@pytest.fixture
def organisation(db, user):
    organisation = Organisation.objects.create(name="Test Organisation", description="A test organisation")
    organisation.users.add(user)
    return organisation

def test_user_cannot_see_other_organisation_data(api_client, user, another_user, organisation):
    api_client.force_authenticate(user=another_user)
    url = f"/api/organisations/{organisation.orgId}/"
    response = api_client.get(url)
    assert response.status_code == 403
