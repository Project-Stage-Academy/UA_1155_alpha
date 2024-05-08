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

class ProjectSerializerUpdate(serializers.ModelSerializer):
    industry = serializers.StringRelatedField()
    """
    Serializer for Project model
    """

    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ('registration_date', 'startup')

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

    def validate(self, data):
        budget_needed = data.get('budget_needed')
        budget_ready = data.get('budget_ready')
        if budget_ready and budget_needed and budget_ready > budget_needed:
            raise serializers.ValidationError(
                {
                    "status": "failed",
                    "message": "Budget ready cannot be greater than budget needed"
                }
            )
        return data


class ProjectViewSerializer(serializers.ModelSerializer):
    """
    Serializer for viewing Project model.
    Returns different fields depending on whether the user is an investor or not.
    """
    industry = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = '__all__'

    @staticmethod
    def get_industry(obj):
        if obj.industry:
            return obj.industry.name
        return None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        if request and hasattr(request.user, 'is_investor') and request.user.is_investor:
            fields_to_exclude = ['updated_at', 'registration_date']
            for field in fields_to_exclude:
                if field in data:
                    del data[field]
            return data
        else:
            fields_to_display = ['project_name', 'description', 'industry']
            filtered_data = {key: data[key] for key in fields_to_display}
            return filtered_data