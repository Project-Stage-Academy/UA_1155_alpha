from rest_framework import serializers
from .models import Startup, Project


class StartupSerializer(serializers.ModelSerializer):
    """
    Serializer for Startup model
    """
    class Meta:
        model = Startup
        fields = ('owner', 'startup_name', 'description', 'industries', 'location', 'contact_phone', 'contact_email',
                  'number_for_startup_validation', 'is_verified', 'registration_date')
        read_only_fields = ('owner', 'registration_date')

    def create(self, validated_data):
        startup = Startup.objects.create(**validated_data)
        return startup


class ProjectSerializer(serializers.ModelSerializer):
    """
    Serializer for Project model
    """
    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ('registration_date', 'startup')

    def create(self, validated_data):
        project = Project.objects.create(**validated_data)
        return project


