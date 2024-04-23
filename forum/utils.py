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
