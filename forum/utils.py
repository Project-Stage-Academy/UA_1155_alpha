"""
Regular expressions for validations in serializers
"""

PASSWORD_REGEX = r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$'
PHONE_NUMBER_REGEX = r'^\+[0-9]{1,3}[0-9]{9}$'
LOCATION_REGEX = r'^([A-Za-z]+[\s,\-]?)+[A-Za-z]+$'
EDRPOU_REGEX = r'^\d{8}$'
FOP_REGEX = r'^\d{10}|\d{12}$'


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
