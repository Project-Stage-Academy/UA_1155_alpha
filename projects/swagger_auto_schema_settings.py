from drf_yasg import openapi
from .serializers import ProjectViewSerializer

project_list_response = {
    '200': openapi.Response(description='List of projects', schema=ProjectViewSerializer)
}

project_retrieve_response = {
    '200': openapi.Response(description='Project details', schema=ProjectViewSerializer)
}

project_create_response = {
    '201': openapi.Response(description='Project created', schema=ProjectViewSerializer),
    '400': "Invalid input"
}

project_delete_response = {
    '204': openapi.Response(description='Project deleted')
}

project_invest_response = {
    '200': openapi.Response(description='Investor added to project'),
    '400': "Bad request"
}

project_subscriber_response = {
    '200': openapi.Response(description='Subscriber added to project'),
    '400': "Bad request"
}

project_compare_response = {
    '200': openapi.Response(description='Comparison result of projects'),
    '400': "Bad request"
}

project_update_response = {
    '200': openapi.Response(description='Project updated', schema=ProjectViewSerializer)
}

project_partial_update_response = {
    '200': openapi.Response(description='Project partially updated', schema=ProjectViewSerializer)
}

project_get_my_projects_response = {
    '200': openapi.Response(description='List of user\'s projects', schema=ProjectViewSerializer)
}
