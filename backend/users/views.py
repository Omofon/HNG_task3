from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Organisation
from .serializers import (
    UserSerializer,
    LoginSerializer,
    UserRegistrationSerializer,
    OrganisationSerializer,
    AddUserToOrganisationSerializer,
)


# Create your views here.
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


class UserRegistrationView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            tokens = get_tokens_for_user(user)
            response_data = {
                "status": "success",
                "message": "Registration successful",
                "data": {
                    "accessToken": tokens["access"],
                    "user": UserSerializer(user).data,
                },
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        except (IntegrityError, ValueError) as e:
            return Response(
                {
                    "status": "Bad request",
                    "message": "Registration unsuccessful",
                    "statusCode": 400,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class UserLoginView(APIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            tokens = serializer.get_tokens(user)
            response_data = {
                "status": "success",
                "message": "Login successful",
                "data": {
                    "accessToken": tokens["access"],
                    "user": UserSerializer(user).data,
                },
            }
            return Response(response_data, status=status.HTTP_200_OK)
        return Response(
            {
                "status": "Bad request",
                "message": "Authentication failed",
                "statusCode": 401,
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )


class UserAdminView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]


class UserDetailView(APIView):
    def get(self, request, user_id, *args, **kwargs):
        try:
            user = User.objects.get(userId=user_id)
            if (
                request.user == user
                or request.user.is_superuser
                or request.user.is_staff
                or Organisation.objects.filter(
                    users=request.user, users__in=[user]
                ).exists()
            ):
                serializer = UserSerializer(user)
                return Response(
                    {
                        "status": "success",
                        "message": "User record retrieved successfully",
                        "data": serializer.data,
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                raise PermissionDenied(
                    "You do not have permission to access this user's record."
                )
        except User.DoesNotExist:
            return Response(
                {"status": "error", "message": "User not found", "statusCode": 404},
                status=status.HTTP_404_NOT_FOUND,
            )


class OrganisationListCreateView(generics.ListCreateAPIView):
    serializer_class = OrganisationSerializer

    def get_queryset(self):
        return Organisation.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {
                "status": "success",
                "message": "Organisations retrieved successfully",
                "data": {"organisations": serializer.data},
            },
            status=status.HTTP_200_OK,
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response(
                {
                    "status": "success",
                    "message": "Organisation created successfully",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {
                "status": "Bad Request",
                "message": "Client error",
                "statusCode": 400,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class OrganisationDetailView(generics.RetrieveAPIView):
    serializer_class = OrganisationSerializer
    lookup_field = "orgId"

    def get_queryset(self):
        return Organisation.objects.filter(users=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        organisation = get_object_or_404(Organisation, orgId=kwargs["orgId"])
        if not organisation.users.filter(id=request.user.id).exists():
            return Response(
                {
                    "detail": "You do not have permission to access this organization's data."
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = self.get_serializer(organisation)
        return Response(
            {
                "status": "success",
                "message": "Organisation retrieved successfully",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class AddUserToOrganisationView(generics.GenericAPIView):
    serializer_class = AddUserToOrganisationSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, orgId):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            organisation = get_object_or_404(Organisation, orgId=orgId)
            user = get_object_or_404(User, userId=serializer.validated_data["userId"])

            organisation.users.add(user)
            organisation.save()

            return Response(
                {
                    "status": "success",
                    "message": "User added to organisation successfully",
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "status": "Bad Request",
                "message": "Client error",
                "statusCode": 400,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
