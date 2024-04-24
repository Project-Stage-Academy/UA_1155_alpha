from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from users.serializers import PasswordResetConfirmSerializer
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser, Investor
from .serializers import UserRegisterSerializer, InvestorSerializer
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


@method_decorator(login_required, name='dispatch')
class InvestorViewSet(viewsets.ViewSet):
    @user_passes_test(lambda user: user.is_staff == 1)
    def list(self, request):
        investors = Investor.objects.all()
        serializer = InvestorSerializer(investors, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @user_passes_test(lambda user: user.is_staff == 1)
    def retrieve(self, request, pk=None):
        try:
            investor = Investor.objects.get(id=pk)
        except Investor.DoesNotExist:
            return Response({'error': 'Investor not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = InvestorSerializer(investor)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @user_passes_test(lambda user: user.is_investor == 1)
    def create(self, request):
        serializer = InvestorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @user_passes_test(lambda user: user.is_investor == 1)
    def update(self, request, pk=None):
        try:
            investor = Investor.objects.get(id=pk)
        except Investor.DoesNotExist:
            return Response({'error': 'Investor not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = InvestorSerializer(instance=investor, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @user_passes_test(lambda user: user.is_investor == 1)
    def partial_update(self, request, pk=None):
        try:
            investor = Investor.objects.get(id=pk)
        except Investor.DoesNotExist:
            return Response({'error': 'Investor not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = InvestorSerializer(instance=investor, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @user_passes_test(lambda user: user.is_investor == 1)
    def destroy(self, request, pk=None):
        try:
            with transaction.atomic():
                investor = Investor.objects.select_related('user').get(id=pk)
                investor.user.is_investor = 0
                investor.user.save()
                investor.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Investor.DoesNotExist:
            return Response({'error': 'Investor not found'}, status=status.HTTP_404_NOT_FOUND)


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

