from rest_framework import serializers

from .models import Startup, Industry
from forum.utils import ValidationPatterns


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

    def to_internal_value(self, data):
        if 'contact_email' in data:
            data['contact_email'] = data['contact_email'].lower()
        return super().to_internal_value(data)

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
        instance.is_verified = validated_data.get('is_verified', instance.is_verified)
        instance.save()
        return instance

    # def validate(self, data):
    #     location = data.get('location')
    #     contact_phone = data.get('contact_phone')
    #     number_for_startup_validation = data.get('number_for_startup_validation')
    #
    #     ValidationPatterns.validate_location(location)
    #
    #     ValidationPatterns.validate_phone_number(contact_phone)
    #
    #     ValidationPatterns.validate_edrpou(number_for_startup_validation)
    #
    #     return data
