from rest_framework import serializers
from .models import Startup


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
        read_only_fields = ('registration_date',)

    def create(self, validated_data):
        return Startup.objects.create(**validated_data)

    def update(self, instance, validated_data):
        required_fields = ['startup_name', 'description', 'industries', 'location', 'contact_phone', 'contact_email']
        missing_fields = [field for field in required_fields if field not in validated_data]
        if missing_fields:
            error_message = f"The following fields are required: {', '.join(missing_fields)}"
            return {'error': error_message}

        instance.startup_name = validated_data.get('startup_name', instance.startup_name)
        instance.description = validated_data.get('description', instance.description)
        instance.industries = validated_data.get('industries', instance.industries)
        instance.location = validated_data.get('location', instance.location)
        instance.contact_phone = validated_data.get('contact_phone', instance.contact_phone)
        instance.contact_email = validated_data.get('contact_email', instance.contact_email)
        instance.number_for_startup_validation = validated_data.get('number_for_startup_validation', instance.number_for_startup_validation)
        instance.save()
        return instance