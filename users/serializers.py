from rest_framework import serializers

from forum.utils import ValidationPatterns
from .models import CustomUser


class UserRegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={"input_type": "password"}, write_only=True)
    profile_img_url = serializers.CharField(required=False)

    class Meta:
        model = CustomUser
        fields = (
            "email",
            "first_name",
            "last_name",
            "password",
            "password2",
            "profile_img_url",
            "is_active_for_proposals",
        )
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def to_internal_value(self, data):
        if 'contact_email' in data:
            data['contact_email'] = data['contact_email'].lower()
        return super().to_internal_value(data)

    def validate(self, data):
        password = data.get("password")
        password2 = data.pop("password2")

        # Check if the password match pattern
        ValidationPatterns.validate_password(password)

        # Check if the passwords match
        ValidationPatterns.validate_passwords_match(password, password2)

        return data


class PasswordResetConfirmSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={"input_type": "password"}, write_only=True)

    class Meta:
        model = CustomUser
        fields = ("password", "password2")
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def validate(self, data):
        password = data.get("password")
        password2 = data.pop("password2")

        ValidationPatterns.validate_password(password)

        ValidationPatterns.validate_passwords_match(password, password2)

        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = (
            "email",
            "first_name",
            "last_name",
            "password",
            "profile_img_url",
            "is_active_for_proposals",
            "is_investor",
            "is_startup",
            "registration_date",
        )
