from django.http import JsonResponse
from rest_framework import status
from rest_framework.views import APIView
from .serializers import StartupSerializer, ProjectSerializer
from rest_framework.response import Response
from .models import Startup


def simple_json_view(request):
    data = {
        'message': 'Hello, STARTUP PAGE',
        'status': 'success'
    }
    return JsonResponse(data)


class CreateStartupAPIView(APIView):
    def post(self, request):
        user = request.user
        if not user.is_startup:
            return Response({'message': 'You\'re not startup'}, status=status.HTTP_400_BAD_REQUEST)
        if Startup.objects.filter(owner=user):
            return Response({'message': 'You\'ve already started a Startup'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = StartupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateProjectAPIView(APIView):
    def post(self, request):
        user = request.user
        startup = Startup.objects.filter(owner=user).first()
        if startup:
            serializer = ProjectSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(owner=user, startup=startup)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": "User doesn't have a startup"}, status=status.HTTP_400_BAD_REQUEST)
