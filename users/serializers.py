import re
from rest_framework import serializers
from users.models import CustomUser


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

        regex_for_password = r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$'

        if not re.match(regex_for_password, password):
            raise serializers.ValidationError({
                'Error': 'Password must contain at least 8 characters, one letter, one number and one special character'})

        if password != password2:
            raise serializers.ValidationError({'Error': 'Passwords do not match'})

        return data
