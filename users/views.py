from django.contrib.sites.shortcuts import get_current_site
from django.http import JsonResponse
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from users.serializers import PasswordResetConfirmSerializer
from forum.utils import get_query_dict
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser
from .serializers import UserRegisterSerializer
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
            'last_name': user.last_name
        })

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=200)

class LogoutAPIView(APIView):
    def post(self, request):
        '''Method should receive "access" and "refresh" tokens in body of POST request to LogOut'''
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'error': 'Refresh token is required.'},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception as e:
            return Response({'error': 'Wrong refresh token.'},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response({'success': 'Successful exit'}, status=status.HTTP_200_OK)


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
                abs_url = 'http://' + current_site + relative_link + '?token=' + str(token)
                email_body = 'Hi ' + custom_user.first_name + ' Use the link below to verify your email \n' + abs_url
                sended_data = {'email_body': email_body, 'email_subject': 'Email confirmation',
                               'to_email': custom_user.email}
                # Util.send_email(data=sended_data)

                return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)
            else:
                return Response({"message": "Failed to create user"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailAPIView(APIView):
    def get(self):
        pass


class InvestorViewSet(viewsets.ViewSet):
    def list(self, request):
        # Implementation of GET METHOD - ExampLE URL: /api/investors/
        # Getting ALL investors logic

        data = {
            'message': "Hello, GET all INVESTORS",
            'status': status.HTTP_200_OK,
        }
        query_data = get_query_dict(request)  # If we need to use queries like /api/investors?name=JamesBond
        if query_data:
            data.update(query_data)

        # Should return a list!
        return Response(data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        # Implementation of GET METHOD for one investor - ExampLE URL: /api/investors/2
        # Getting ONE investor with investors_id=pk logic

        investor_id = pk
        data = {
            'investor_id': investor_id,
            'message': f"Hello, concrete INVESTOR profile page with id {investor_id}",
            'status': status.HTTP_200_OK
        }
        query_data = get_query_dict(request)  # If we need to use queries like /api/investors?name=JamesBond
        if query_data:
            data.update(query_data)

        return Response(data, status=status.HTTP_200_OK)

    def create(self, request):
        # Implementation of POST METHOD for one investor - ExampLE URL: /api/investors/
        # Do not forget slash at the end of link
        # + you should send data in JSON
        # Creating investor logic
        investor_info = request.data
        data = {
            'message': "You successfully POSTed new INVESTOR",
            'investor_info': investor_info,
            'status': status.HTTP_200_OK
        }
        return Response(data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        # Implementation of PUT METHOD for one investor - ExampLE URL: /api/investors/2/
        # Do not forget about SLASH at the end of URL
        # + you should send data in JSON
        investor_id = pk
        investor_updated_info = request.data
        # ...
        # PUT logic
        # ...
        data = {
            'investor_id': investor_id,
            'message': f"Hello, here's a PUT method! You update ALL information about INVESTOR № {investor_id}",
            'updated_data': investor_updated_info,
            'status': status.HTTP_200_OK
        }
        return Response(data, status=status.HTTP_200_OK)

    def partial_update(self, request, pk=None):
        # Implementation of PATCH METHOD for one investor - ExampLE URL: /api/investors/2/
        # Do not forget about SLASH at the end of URL
        # + you should send data in JSON
        # PATCHcing logic
        investor_id = pk
        investor_specific_updated_info = request.data
        data = {
            'investor_id': investor_id,
            'message': f"Hello, here's a PATCH method! You updated SOME information about INVESTOR № {investor_id}",
            'specific_updated_data': investor_specific_updated_info,
            'status': status.HTTP_200_OK
        }
        return Response(data, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        # Implementation of DELETE METHOD for one investor - ExampLE URL: /api/investors/4/
        # Do not forget about SLASH at the end of URL
        # Deleting logic
        investor_id = pk
        data = {
            'investor_id': investor_id,
            'message': f"Hello, you DELETED INVESTOR with ID: {investor_id}",
            'status': status.HTTP_200_OK
        }
        return Response(data, status=status.HTTP_204_NO_CONTENT)


class PasswordResetRequest(APIView):
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User with this email does not exist'}, status=status.HTTP_404_NOT_FOUND)

        token = RefreshToken.for_user(user)
        current_site = get_current_site(request).domain
        relative_link = reverse('password_reset_confirm',
                                kwargs={'token': token, 'uidb64': urlsafe_base64_encode(force_bytes(user.id))})
        abs_url = 'http://' + current_site + relative_link

        subject = 'Password Reset Request'
        message = f'Hi {user.first_name},\n\nTo reset your password, click the link below:\n\n{abs_url}'
        sended_data = {'email_body': message, 'email_subject': subject, 'to_email': user.email}
        Util.send_email(data=sended_data)

        return Response({'message': 'Password reset email sent'}, status=status.HTTP_200_OK)


class PasswordResetConfirm(APIView):
    def post(self, request, uidb64, token):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            new_password = validated_data.get('password')

            try:
                uid = urlsafe_base64_decode(uidb64).decode()
                user = CustomUser.objects.get(pk=uid)
            except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
                return Response({'error': 'Invalid user ID'}, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(new_password)
            user.save()
            return Response({'message': 'Password reset successfully'}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

