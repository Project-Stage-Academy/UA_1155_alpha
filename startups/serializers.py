from rest_framework import serializers
from .models import Startup


class StartupSerializer(serializers.ModelSerializer):
    """
    Serializer for Startup model
    """
    class Meta:
        model = Startup
        fields = ('owner', 'startup_name', 'description', 'industries', 'location', 'contact_phone', 'contact_email',
                  'number_for_startup_validation', 'is_verified', 'registration_date')
        read_only_fields = ('owner', 'registration_date')


