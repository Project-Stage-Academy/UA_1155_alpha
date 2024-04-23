from rest_framework import serializers
from .models import Project


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
