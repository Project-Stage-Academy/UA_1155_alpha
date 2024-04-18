from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from users.serializers import CustomUserSerializer
from users.models import CustomUser


# # def simple_json_view_users(request):
#     data = {
#         'message': 'Hello, USER PAGE',
#         'status': 'success'
#     }
#     return JsonResponse(data)

@api_view(['POST'])
def login_api(request):
    email = request.data.get('email')
    password = request.data.get('password')
    user = CustomUser.objects.filter(email=email).first()
    if not user:
        return Response({"message": "User not found"})
    if not user.check_password(password):
        return Response({"message": "Wrong password"})

    refresh = RefreshToken.for_user(user)
    refresh.payload.update({
    'email': user.email,
    'password': user.password
    })

    return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=200)
