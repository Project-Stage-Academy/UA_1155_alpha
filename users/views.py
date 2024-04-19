from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser
from .serializers import UserRegisterSerializer
from rest_framework.decorators import api_view
from django.shortcuts import render
from django.http import JsonResponse


class LoginAPIView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = CustomUser.objects.filter(email=email).first()

        if not user:
            return Response({"message": "User not found"}, status=status.HTTP_400_BAD_REQUEST)
        if not user.check_password(password):
            return Response({"message": "Wrong password"}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)
        refresh.payload.update({
        'id': user.id,
        'username': user.username
        })

        return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=200)
        
        
@api_view(['POST'])
def register_user(request):
    if request.method == 'POST':
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
