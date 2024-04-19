from .models import CustomUser, Investor
from rest_framework import serializers

class UserRegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    
    class Meta:
        model = CustomUser
        fields = ['email', 
                  'username', 
                  'password', 
                  'password2',
                  'is_email_valid', 
                  'profile_img_url', 
                  'is_active_for_proposals',
                  'is_investor',
                  'is_startup',
                  'is_active',
                  'is_staff',
                  'registration_date']
        extra_kwargs = {'password': {'write_only': True}, 'registration_date': {'required': False}}
        
    def create(self, validated_data):
        password = validated_data['password']
        password2 = validated_data['password2']
        
        # Check if the passwords match
        if password != password2:
            raise serializers.ValidationError({'Error': 'Passwords do not match'})
        
        # Creating new user
        user_manager = CustomUser.objects
        user = user_manager.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            username=validated_data['username'],
            is_email_valid=validated_data.get('is_email_valid', False),
            profile_img_url=validated_data.get('profile_img_url', ''),
            is_active_for_proposals=validated_data.get('is_active_for_proposals', False),
            is_investor=validated_data.get('is_investor', False),
            is_startup=validated_data.get('is_startup', False),
            is_active=validated_data.get('is_active', True),
            is_staff=validated_data.get('is_staff', False)
        )
        
        return user

                