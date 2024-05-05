import re
from rest_framework import serializers


class ValidationPatterns:
    """
    Class for validations in serializers
    """

    PASSWORD_REGEX = r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$'
    PHONE_NUMBER_REGEX = r'^\+[0-9]{1,3}[0-9]{9}$'
    LOCATION_REGEX = r'^([A-Za-z]+[\s,\-]?)+[A-Za-z]+$'
    EDRPOU_REGEX = r'^\d{8}$'
    FOP_REGEX = r'^\d{10}|\d{12}$'

    @staticmethod
    def validate_password(password):
        if not re.match(ValidationPatterns.PASSWORD_REGEX, password):
            raise serializers.ValidationError({
                'Error': 'Password must contain at least 8 characters, 1 letter, 1 number and 1 special character'})

    @staticmethod
    def validate_passwords_match(password, password2):
        if password != password2:
            raise serializers.ValidationError({"Error": "Passwords do not match"})

    @staticmethod
    def validate_phone_number(phone_number):
        if not re.match(ValidationPatterns.PHONE_NUMBER_REGEX, phone_number):
            raise serializers.ValidationError({'Error': 'Mobile phone number must be in the format +XXXXXXXXXX'})

    @staticmethod
    def validate_location(location):
        if not re.match(ValidationPatterns.LOCATION_REGEX, location):
            raise serializers.ValidationError({
                "Error": "Location must be in the format 'Name Region' or 'Name, Region' and in English"})
        if not location[0].isupper():
            raise serializers.ValidationError({"Error": "Region name must start with an uppercase letter"})

    @staticmethod
    def validate_edrpou(edrpou):
        if not re.match(ValidationPatterns.EDRPOU_REGEX, str(edrpou)):
            raise serializers.ValidationError({"Error": "EDRPOU code must contain exactly 8 digits"})

    @staticmethod
    def validate_fop(fop):
        if not re.match(ValidationPatterns.FOP_REGEX, str(fop)):
            raise serializers.ValidationError({'Error': 'FOP code must contain 10 or 12 digits'})


def get_query_dict(request):
    """
    The get_query_dict function takes in a request object and returns a dictionary of the query parameters.

    :param request: Get the query parameters from the request object
    :return: A dictionary of all the query parameters in a request
    """
    query_data = {}
    query_params = request.GET
    for key, value in query_params.items():
        query_data[key] = value
    return query_data
