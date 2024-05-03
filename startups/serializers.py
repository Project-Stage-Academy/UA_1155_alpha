from rest_framework import serializers
import re

from .models import Startup, Industry


class StartupListSerializer(serializers.ModelSerializer):
    industries = serializers.CharField(source='industries.name')
    class Meta:
        model = Startup
        fields = ('startup_name',
                  'description',
                  'industries',
                  'location',
                  'contact_phone',
                  'contact_email',
                  'registration_date',
                  )


class StartupSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(
        read_only=True
    )

    class Meta:
        model = Startup
        fields = '__all__'
        read_only_fields = ('registration_date', 'owner')

    def create(self, validated_data):
        user = self.context['request'].user
        user.is_startup = True
        user.save()
        if 'owner' not in validated_data:
            validated_data['owner'] = user
        startup = Startup.objects.create(**validated_data)
        return startup


class StartupSerializerUpdate(serializers.ModelSerializer):
    industries = serializers.StringRelatedField()
    owner = serializers.PrimaryKeyRelatedField(
        read_only=True
    )

    class Meta:
        model = Startup
        fields = '__all__'
        read_only_fields = ('registration_date', 'owner')


    def update(self, instance, validated_data):
        instance.startup_name = validated_data.get('startup_name', instance.startup_name)
        instance.description = validated_data.get('description', instance.description)
        instance.industries = validated_data.get('industries', instance.industries)
        instance.location = validated_data.get('location', instance.location)
        instance.contact_phone = validated_data.get('contact_phone', instance.contact_phone)
        instance.contact_email = validated_data.get('contact_email', instance.contact_email)
        instance.number_for_startup_validation = validated_data.get('number_for_startup_validation', instance.number_for_startup_validation)
        instance.save()
        return instance

    def validate_location(self, data):
        # Check if location consists of two or more words separated by space, comma, or hyphen,
        # where all words contain only English letters
        if not re.match(r'^([A-Za-z]+[\s,\-]?)+[A-Za-z]+$', data):
            raise serializers.ValidationError(
                "Location must be in the format 'Name Region' or 'Name, Region' and contain only English letters")
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
