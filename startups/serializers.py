from rest_framework import serializers
from .models import Startup, Project
import re


class StartupListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Startup
        fields = ('startup_name',
                  'description',
                  'industries',
                  'location',
                  'contact_phone',
                  'contact_email')


class StartupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Startup
        fields = '__all__'
        read_only_fields = ('registration_date', )

    def create(self, validated_data):
        return Startup.objects.create(**validated_data)

    def validate_location(self, data):
        # Check if location consists of two or more words separated by space, comma, or hyphen,
        # where all words contain only English letters
        if not re.match(r'^([A-Za-z]+[\s,\-]?)+[A-Za-z]+$', data):
            raise serializers.ValidationError("Location must be in the format 'Name Region' or 'Name, Region' and contain only English letters")
        # Check if the first word starts with an uppercase letter
        if not data[0].isupper():
            raise serializers.ValidationError("Region name must start with an uppercase letter")
        return data

    def validate_contact_phone(self, data):
        if not re.match(r'^\d{3}-\d{3}-\d{4}$', data):
            raise serializers.ValidationError("Mobile phone number must be in the format XXX-XXX-XXXX")
        return data

    def validate_contact_email(self, data):
        regex_for_email = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        # Check if the email match pattern
        if not re.match(regex_for_email, data):
            raise serializers.ValidationError({"Error": "Invalid email address"})
        return data

    def validate_number_for_startup_validation(self, data):
        # Convert data to string
        data_str = str(data)
        # Check if the EDRPOU code consists of exactly 8 digits
        if not re.match(r'^\d{8}$', data_str):
            raise serializers.ValidationError("EDRPOU code must contain exactly 8 digits")
        return data


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

    def update(self, instance, validated_data):
        instance.project_name = validated_data.get('project_name', instance.project_name)
        instance.description = validated_data.get('description', instance.description)
        instance.goals = validated_data.get('goals', instance.goals)
        instance.status = validated_data.get('status', instance.status)
        instance.budget_needed = validated_data.get('budget_needed', instance.budget_needed)
        instance.budget_ready = validated_data.get('budget_ready', instance.budget_ready)
        instance.industry = validated_data.get('industry', instance.industry)
        instance.promo_photo_url = validated_data.get('promo_photo_url', instance.promo_photo_url)
        instance.promo_video_url = validated_data.get('promo_video_url', instance.promo_video_url)
        instance.save()
        return instance
