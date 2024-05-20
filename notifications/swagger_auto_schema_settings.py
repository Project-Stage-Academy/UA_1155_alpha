from drf_yasg import openapi
from rest_framework import status

new_notifications_response = {
    200: openapi.Response(
        description="A list of new notifications.",
        schema=openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'project_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'send_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
                    'text': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )
        )
    ),
    404: openapi.Response(description="You do not have new notifications.")
}

all_notifications_response = {
    200: openapi.Response(
        description="A list of all notifications.",
        schema=openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'project_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'send_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
                    'text': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )
        )
    ),
    404: openapi.Response(description="You do not have new notifications.")
}
