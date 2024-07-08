from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserRegistrationView,
    UserLoginView,
    UserDetailView,
    UserAdminView,
    OrganisationListCreateView,
    OrganisationDetailView,
    AddUserToOrganisationView,
)

router = DefaultRouter()
router.register(r"api/admin/users", UserAdminView, basename="user-admin")

urlpatterns = [
    path("", include(router.urls)),
    path("auth/register", UserRegistrationView.as_view(), name="register"),
    path("auth/login", UserLoginView.as_view(), name="login"),
    path("api/users/<uuid:user_id>", UserDetailView.as_view(), name="user-detail"),
    path(
        "api/organisations",
        OrganisationListCreateView.as_view(),
        name="organisation-list-create",
    ),
    path(
        "api/organisations/<uuid:orgId>",
        OrganisationDetailView.as_view(),
        name="organisation-detail",
    ),
    path(
        "api/organisations/<str:orgId>/users",
        AddUserToOrganisationView.as_view(),
        name="add-user-to-organisation",
    ),
]
