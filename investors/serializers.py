import re
from rest_framework import serializers
from .models import Investor
from forum.utils import PHONE_NUMBER_REGEX, FOP_REGEX


class InvestorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Investor
        fields = '__all__'
        read_only_fields = ('user',)

    def validate(self, data):
        number = data.get('contact_phone')
        fop_code = data.get('number_for_investor_validation')

        if not re.match(PHONE_NUMBER_REGEX, number):
            raise serializers.ValidationError({'Error': 'Phone number is not correct'})

        if not re.match(FOP_REGEX, fop_code):
            raise serializers.ValidationError({'Error': 'FOP code must contain 10 or 12 digits'})

        return data
