import re
from rest_framework import serializers
from .models import Investor


class InvestorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Investor
        fields = '__all__'

    def validate(self, data):
        number = data.get('contact_phone')
        regex_for_number = r'^\+[0-9]{1,3}[0-9]{9}$'

        if not re.match(regex_for_number, number):
            raise serializers.ValidationError({'Error': 'Phone number is not correct'})

        return data