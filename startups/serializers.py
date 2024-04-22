from rest_framework import serializers
from .models import Startup, Project


class StartupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Startup
        fields = ('startup_name',
                  'description',
                  'industries',
                  'location',
                  'contact_phone',
                  'contact_email',
                  'number_for_startup_validation',
                  'owner'
                  )

class StartupListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Startup
        fields = ('startup_name',
                  'description',
                  'industries',
                  'location',
                  'contact_phone',
                  'contact_email')