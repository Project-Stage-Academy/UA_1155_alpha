from rest_framework import serializers
from .models import Investor
from forum.utils import ValidationPatterns


class InvestorSerializer(serializers.ModelSerializer):
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

        ValidationPatterns.validate_phone_number(number)

        ValidationPatterns.validate_fop(fop_code)

        if investment_amount <= 0:
            raise serializers.ValidationError({'Error': 'Investment amount must be greater than 0'})

        return data
