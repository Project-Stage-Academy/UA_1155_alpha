from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import viewsets

from .models import CustomUser
from .serializers import CustomUserSerializer


class CustomUserView(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

# def simple_json_view_users(request):
#     data = {
#         'message': 'Hello, USER PAGE',
#         'status': 'success'
#     }
#     return JsonResponse(data)


