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
        fields = ('startup_name',
                  'description',
                  'industries',
                  'location',
                  'contact_phone',
                  'contact_email',
                  'number_for_startup_validation')
        read_only_fields = ('registration_date', 'owner')

    def create(self, validated_data):
        return Startup.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.startup_name = validated_data.get('startup_name', instance.startup_name)
        instance.description = validated_data.get('description', instance.description)
        instance.industries = validated_data.get('industries', instance.industries)
        instance.location = validated_data.get('location', instance.location)
        instance.contact_phone = validated_data.get('contact_phone', instance.contact_phone)
        instance.contact_email = validated_data.get('contact_email', instance.contact_email)
        instance.number_for_startup_validation = validated_data.get('number_for_startup_validation', instance.number_for_startup_validation)
        if all([field in validated_data for field in self.fields]):
            instance.save()
            return instance
        else:
            raise serializers.ValidationError("All fields are required for full update")