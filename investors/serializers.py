from rest_framework import serializers

from forum.utils import ValidationPatterns
from startups.models import Industry
from .models import Investor


class IndustryNameField(serializers.RelatedField):
    def to_representation(self, value):
        return value.name

    def to_internal_value(self, data):
        try:
            industry = Industry.objects.get(name=data)
        except Industry.DoesNotExist:
            raise serializers.ValidationError(f"Industry with name '{data}' does not exist.")
        return industry


class InvestorSerializer(serializers.ModelSerializer):
    interests = serializers.SlugRelatedField(
        queryset=Industry.objects.all(),
        slug_field='name',
        many=True)


    class Meta:
        model = Investor
        fields = '__all__'
        read_only_fields = ('user',)

    def to_internal_value(self, data):
        if 'contact_email' in data:
            data['contact_email'] = data['contact_email'].lower()
        return super().to_internal_value(data)

    def validate(self, data):
        number = data.get('contact_phone')
        fop_code = data.get('number_for_investor_validation')
        investment_amount = data.get('investment_amount')

        if number:
            ValidationPatterns.validate_phone_number(number)

        if fop_code:
            ValidationPatterns.validate_fop(fop_code)

        if investment_amount is not None and investment_amount <= 0:
            raise serializers.ValidationError({'Error': 'Investment amount must be greater than 0'})

        return data


class InvestorCreateSerializer(serializers.ModelSerializer):
    interests = serializers.SlugRelatedField(
        queryset=Industry.objects.all(),
        slug_field='name',
        many=True
    )

    class Meta:
        model = Investor
        fields = ['user', 'location', 'contact_phone', 'contact_email', 'investment_amount', 'interests',
                  'number_for_investor_validation', 'is_active']

    def create(self, validated_data):
        interests_data = validated_data.pop('interests', [])
        industries = []
        for name in interests_data:
            try:
                industry = Industry.objects.get(name=name)
                industries.append(industry)
            except Industry.DoesNotExist:
                raise serializers.ValidationError(f"Industry '{name}' does not exist")

        investor = Investor.objects.create(**validated_data)
        investor.interests.set(industries)

        return investor

