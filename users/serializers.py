import re
from rest_framework import serializers

from forum.utils import PASSWORD_REGEX
from .models import CustomUser


class UserRegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    profile_img_url = serializers.CharField(required=False)

    class Meta:
        model = CustomUser
        fields = ('email',
                  'first_name',
                  'last_name',
                  'password',
                  'password2',
                  'profile_img_url',
                  'is_active_for_proposals',
                  'is_investor',
                  'is_startup')
        extra_kwargs = {'password': {'write_only': True}, }

    def validate(self, data):
        email = data.get("email")
        password = data.get('password')
        password2 = data.pop('password2')

        # Check if the passwords match pattern
        if not re.match(PASSWORD_REGEX, password):
            raise serializers.ValidationError({
                'Error': 'Password must contain at least 8 characters, one letter, one number and one special character'})

        # Check if the passwords match
        if password != password2:
            raise serializers.ValidationError({'Error': 'Passwords do not match'})

        # Check if user with the same email already exists
        if CustomUser.objects.filter(email=email).exists():
            raise serializers.ValidationError({"Error": "Email already exist"})

        return data


class PasswordResetConfirmSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = CustomUser
        fields = ('password',
                  'password2')
        extra_kwargs = {'password': {'write_only': True}, }

    def validate(self, data):
        password = data.get('password')
        password2 = data.pop('password2')

        if not re.match(PASSWORD_REGEX, password):
            raise serializers.ValidationError({
                'Error': 'Password must contain at least 8 characters, one letter, one number and one special character'})

        if password != password2:
            raise serializers.ValidationError({'Error': 'Passwords do not match'})

        return data
