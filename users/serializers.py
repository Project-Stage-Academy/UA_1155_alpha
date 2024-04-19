from .models import CustomUser, Investor
from rest_framework import serializers

class UserRegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    
    class Meta:
        model = CustomUser
        fields = ['id',
                  'email', 
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
        extra_kwargs = {'password': {'write_only': True}}
        
      
    def create(self):
        password = self.validated_data['password']  
        password2 = self.validated_data['password2']  
        
        if password != password2:
            raise serializers.ValidationError({'Error': 'Passwords do not match'})
        
        if self.objects.filter(email=self.validated_data['email']).exists():
             raise ValueError('User with this email already exist.')

        if CustomUser.objects.filter(username=self.validated_data['username']).exists():
            raise ValueError('User with this username already exist.')
        
        user = CustomUser(
            username=self.validated_data['username'],
            email=self.validated_data['email']
        )
        user.set_password(self.validated_data['password'])
        user.save()
        return user
                