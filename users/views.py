from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser
from .serializers import UserRegisterSerializer
from rest_framework.permissions import IsAuthenticated
from .utils import Util
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse


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
        'first_name': user.first_name,
        'surname': user.surname
        })

        return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=200)
        
        
class UserRegisterAPIView(APIView):
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            custom_user = CustomUser.create_user(**validated_data)
            if custom_user:
                
                token = RefreshToken.for_user(custom_user).access_token
                current_site = get_current_site(request).domain
                relative_link = reverse('send_email_confirmation')
                abs_url = 'http://'+ current_site + relative_link + '?token=' + str(token)
                email_body = 'Hi ' + custom_user.first_name + ' Use the link below to verify your email \n' + abs_url
                sended_data = {'email_body': email_body, 'email_subject': 'Email confirmation', 'to_email': custom_user.email}
                # Util.send_email(data=sended_data)
                
                return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)
            else:
                return Response({"message": "Failed to create user"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailAPIView(APIView):
    def get(self):
        pass