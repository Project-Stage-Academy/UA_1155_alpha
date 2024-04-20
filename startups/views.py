from django.http import JsonResponse
from rest_framework import status
from rest_framework.views import APIView
from .serializers import StartupSerializer
from rest_framework.response import Response


def simple_json_view(request):
    data = {
        'message': 'Hello, STARTUP PAGE',
        'status': 'success'
    }
    return JsonResponse(data)


class CreateStartupAPIView(APIView):
    def post(self, request):
        user = request.user
        serializer = StartupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




