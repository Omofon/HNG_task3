from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers
from .models import User, Organisation


class UserSerializer(serializers.ModelSerializer):
    userId = serializers.UUIDField(read_only=True)

    class Meta:
        model = User
        fields = ["userId", "firstName", "lastName", "email", "phone"]


class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["firstName", "lastName"]


class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["firstName", "lastName", "password", "email", "phone"]
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def validate(self, data):
        errors = []
        if not data.get("firstName"):
            errors.append(
                {"field": "firstName", "message": "First Name must not be null"}
            )
        if not data.get("lastName"):
            errors.append(
                {"field": "lastName", "message": "Last Name must not be null"}
            )
        if not data.get("email"):
            errors.append({"field": "email", "message": "Email must not be null"})
        if not data.get("password"):
            errors.append({"field": "password", "message": "Password must not be null"})

        if errors:
            raise serializers.ValidationError({"errors": errors})
        return data

    def create(self, validated_data):
        user = User(
            email=validated_data["email"],
            firstName=validated_data["firstName"],
            lastName=validated_data["lastName"],
            phone=validated_data.get("phone", ""),
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        if email and password:
            user = authenticate(
                request=self.context.get("request"), email=email, password=password
            )
            if not user:
                raise serializers.ValidationError(
                    "Invalid email or password", code="authorization"
                )
        else:
            raise serializers.ValidationError(
                'Must include "email" and "password"', code="authorization"
            )

        data["user"] = user
        return data

    def get_tokens(self, user):
        refresh = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }


class OrganisationSerializer(serializers.ModelSerializer):
    name = serializers.CharField(read_only=True)

    class Meta:
        model = Organisation
        fields = ["orgId", "name", "description"]

    def naming_org(self, user: User):
        return f"{user.firstName}'s Organisation"

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["name"] = self.naming_org(user)
        organisation = Organisation.objects.create(**validated_data)
        organisation.users.add(user)
        return organisation


class AddUserToOrganisationSerializer(serializers.Serializer):
    userId = serializers.UUIDField()

    def validate_userId(self, value):
        try:
            user = User.objects.get(userId=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User does not exist.")
        return value
