from drf_yasg import openapi
from .serializers import InvestorSerializer
from rest_framework import status

fetch_list_of_all_users_responses_GET = {
    200: openapi.Response(
        description="A list of active investors.",
        schema=openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Investor ID'),
                    'name': openapi.Schema(type=openapi.TYPE_STRING, description='Investor name'),
                    'email': openapi.Schema(type=openapi.TYPE_STRING, description='Investor email'),
                    # Додайте інші поля, що входять у вашого серіалізатора
                }
            )
        ),
        examples={
            "application/json": [
                {"id": 1, "name": "John Doe", "email": "john.doe@example.com"},
                {"id": 2, "name": "Jane Smith", "email": "jane.smith@example.com"},
                # Додайте більше прикладів за потреби
            ]
        }
    ),
    400: openapi.Response(
        description="Bad request.",
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
            }
        ),
        examples={
            "application/json": {
                "error": "Invalid request"
            }
        }
    ),
}


fetch_particular_investor_GET = {
    200: openapi.Response(
        description="Your investor.",
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'message': openapi.Schema(type=openapi.TYPE_STRING, description='Response message'),
                'investor': openapi.Schema(type=openapi.TYPE_OBJECT, description='Investor details', properties={
                    'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Investor ID'),
                    'name': openapi.Schema(type=openapi.TYPE_STRING, description='Investor name'),
                    'email': openapi.Schema(type=openapi.TYPE_STRING, description='Investor email'),
                })
            }
        ),
        examples={
            "application/json": {
                "message": "Your investor",
                "investor": {
                    "id": 1,
                    "name": "John Doe",
                    "email": "john.doe@example.com"
                }
            }
        },
    ),
    404: openapi.Response(
        description="Your investor not found.",
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
            }
        ),
        examples={
            "application/json": {
                "error": "Investor not found"
            }
        },
    ),
}

fetch_create_investor_body_POST = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['contact_email', 'investment_amount', 'number_for_investor_validation'],  
    properties={
        'contact_email': openapi.Schema(type=openapi.TYPE_STRING, description='Investor contact email'),
        'investment_amount': openapi.Schema(type=openapi.TYPE_NUMBER, description='Investment amount'),
        'number_for_investor_validation': openapi.Schema(type=openapi.TYPE_INTEGER, description='Number for investor validation'),
        'location': openapi.Schema(type=openapi.TYPE_STRING, description='Investor location'),
        'contact_phone': openapi.Schema(type=openapi.TYPE_STRING, description='Investor contact phone'),
        'interests': openapi.Schema(type=openapi.TYPE_STRING, description='Investor interests'),
        'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Investor is active'),
    }
)



fetch_create_investor_responses_POST = {
    201: openapi.Response(
        description="Investor created successfully.",
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Investor ID'),
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='Investor name'),
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='Investor email'),
                # Додайте інші поля, що входять у вашого серіалізатора
            }
        ),
        examples={
            "application/json": {
                "id": 1,
                "name": "John Doe",
                "email": "john.doe@example.com",
                # Додайте інші приклади полів
            }
        }
    ),
    400: openapi.Response(
        description="Bad request.",
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
            }
        ),
        examples={
            "application/json": {
                "error": "Investor already exists for this user",
                # Або інші можливі помилки валідації
            }
        }
    ),
    401: openapi.Response(
        description="Bad request.",
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
            }
        ),
        examples={
            "application/json": {
                "detail": "Authentication credentials were not provided.",
                # Або інші можливі помилки валідації
            }
        }
    ),
}

fetch_update_investor_body_PUT = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'contact_email': openapi.Schema(type=openapi.TYPE_STRING, description='New investor contact email'),
        'investment_amount': openapi.Schema(type=openapi.TYPE_NUMBER, description='New investment amount'),
        'number_for_investor_validation': openapi.Schema(type=openapi.TYPE_INTEGER, description='New number for investor validation'),
        'location': openapi.Schema(type=openapi.TYPE_STRING, description='New investor location'),
        'contact_phone': openapi.Schema(type=openapi.TYPE_STRING, description='New investor contact phone'),
        'interests': openapi.Schema(type=openapi.TYPE_STRING, description='New investor interests'),
        # Додайте інші поля, які можна оновити
    }
)

# Визначення прикладів відповідей для оновлення інвестора
fetch_update_investor_responses_PUT = {
    200: openapi.Response(
        description="Investor updated successfully.",
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Investor ID'),
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='Investor name'),
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='Investor email'),
                # Додайте інші поля, що входять у вашого серіалізатора
            }
        ),
        examples={
            "application/json": {
                "id": 1,
                "name": "John Doe",
                "email": "john.doe@example.com",
                # Додайте інші приклади полів
            }
        }
    ),
    400: openapi.Response(
        description="Bad request.",
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
            }
        ),
        examples={
            "application/json": {
                "error": "Invalid data",
                # Або інші можливі помилки валідації
            }
        }
    ),
}
fetch_partial_update_investor_body_PATCH = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'contact_email': openapi.Schema(type=openapi.TYPE_STRING, description='New investor contact email'),
        'investment_amount': openapi.Schema(type=openapi.TYPE_NUMBER, description='New investment amount'),
        'number_for_investor_validation': openapi.Schema(type=openapi.TYPE_INTEGER, description='New number for investor validation'),
        'location': openapi.Schema(type=openapi.TYPE_STRING, description='New investor location'),
        'contact_phone': openapi.Schema(type=openapi.TYPE_STRING, description='New investor contact phone'),
        'interests': openapi.Schema(type=openapi.TYPE_STRING, description='New investor interests'),
        # Додайте інші поля, які можна частково оновити
    }
)

# Визначення прикладів відповідей для часткового оновлення інвестора
fetch_partial_update_investor_responses_PATCH = {
    200: openapi.Response(
        description="Investor updated successfully.",
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Investor ID'),
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='Investor name'),
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='Investor email'),
                # Додайте інші поля, що входять у вашого серіалізатора
            }
        ),
        examples={
            "application/json": {
                "id": 1,
                "name": "John Doe",
                "email": "john.doe@example.com",
                # Додайте інші приклади полів
            }
        }
    ),
    400: openapi.Response(
        description="Bad request.",
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
            }
        ),
        examples={
            "application/json": {
                "error": "Invalid data",
                # Або інші можливі помилки валідації
            }
        }
    ),
}

fetch_destroy_investor_responses_DELETE = {
    204: openapi.Response(
        description="Investor deactivated successfully.",
    ),
    404: openapi.Response(
        description="Investor not found.",
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'detail': openapi.Schema(type=openapi.TYPE_STRING, description='Not found error message')
            }
        ),
        examples={
            "application/json": {
                "detail": "Not found."
            }
        }
    ),
}

fetch_all_subscribed_projects_responses_GET = {
    200: openapi.Response(
        description="List of subscribed projects.",
        schema=openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Project ID'),
                    'name': openapi.Schema(type=openapi.TYPE_STRING, description='Project name'),
                    # Додайте інші поля проекту
                }
            )
        ),
        examples={
            "application/json": [
                {"id": 1, "name": "Project Alpha"},
                {"id": 2, "name": "Project Beta"},
                # Додайте інші приклади проектів
            ]
        }
    ),
    404: openapi.Response(
        description="Investor not found.",
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
            }
        ),
        examples={
            "application/json": {
                "error": "Investor not found"
            }
        }
    ),
}


fetch_remove_subscribed_project_responses_POST = {
    200: openapi.Response(
        description="Project successfully removed from subscribed projects.",
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'message': openapi.Schema(type=openapi.TYPE_STRING, description='Success message')
            }
        ),
        examples={
            "application/json": {
                "message": "Project 1 successfully removed from subscribed projects"
            }
        }
    ),
    404: openapi.Response(
        description="Investor or Project not found.",
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
            }
        ),
        examples={
            "application/json": {
                "error": "Investor not found"
            }
        }
    ),
}

remove_subscribed_project_body_POST = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['project_id'],
    properties={
        'project_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the project to be removed')
    },
    example={
        'project_id': 1
    }
)


fetch_my_profile_responses_GET = {
    200: openapi.Response(
        description="Investor profile retrieved successfully.",
        schema=InvestorSerializer,
        examples={
            "application/json": {
                "id": 1,
                "user": 1,
                "location": "Kyiv",
                "contact_phone": "+380123456789",
                "contact_email": "investor@example.com",
                "investment_amount": "100000.00",
                "interests": "Technology, Healthcare",
                "number_for_investor_validation": 123456,
                "is_active": True
            }
        }
    ),
    404: openapi.Response(
        description="Investor not found.",
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
            }
        ),
        examples={
            "application/json": {
                "error": "Investor not found"
            }
        }
    ),
}