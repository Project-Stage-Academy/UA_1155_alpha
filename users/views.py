import jwt
from django.contrib.sites.shortcuts import get_current_site
from django.db.models.functions import Now
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

# from investors.views import InvestorProfileView
from users.serializers import PasswordResetConfirmSerializer, UserSerializer

from .models import CustomUser
from .serializers import UserRegisterSerializer
from .utils import Util


class LoginAPIView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        user = CustomUser.objects.filter(email=email).first()

        if not user:
            return Response(
                {"message": "User not found"}, status=status.HTTP_400_BAD_REQUEST
            )
        if not user.check_password(password):
            return Response(
                {"message": "Wrong password"}, status=status.HTTP_401_UNAUTHORIZED
            )

        user.last_login = Now()
        user.save()

        refresh = RefreshToken.for_user(user)
        refresh.payload.update(
            {"id": user.id, "first_name": user.first_name, "last_name": user.last_name}
        )

        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=200,
        )


class LogoutAPIView(APIView):
    def post(self, request):
        """Method should receive "access" and "refresh" tokens in body of POST request to LogOut"""
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"error": "Refresh token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception as e:
            return Response(
                {"error": "Wrong refresh token."}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response({"success": "Successful exit"}, status=status.HTTP_200_OK)


class UserRegisterAPIView(APIView):
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            custom_user = CustomUser.create_user(**validated_data)
            if custom_user:

                token = RefreshToken.for_user(custom_user).access_token
                current_site = get_current_site(request).domain
                relative_link = reverse(
                    "verify-email",
                    kwargs={
                        "token": token,
                    },
                )
                abs_url = f"http://{current_site}{relative_link}"
                email_body = (
                    "Hi "
                    + custom_user.first_name
                    + " Use the link below to verify your email \n"
                    + abs_url
                )
                sended_data = {
                    "email_body": email_body,
                    "email_subject": "Email confirmation",
                    "to_email": custom_user.email,
                }
                Util.send_email(data=sended_data)

                return Response(
                    {
                        "User name": custom_user.first_name,
                        "message": "User created successfully",
                    },
                    status=status.HTTP_201_CREATED,
                )
            else:
                return Response(
                    {"message": "Failed to create user"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SendEmailConfirmationAPIView(APIView):

    def get(self, request, token=None):
        return Response(
            {"message": "Plese, confifm your email"}, status=status.HTTP_200_OK
        )

    def post(self, request, token=None):
        if not token:
            return Response(
                {"message": "You need a token to verify email."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            decoded_token = jwt.decode(token, options={"verify_signature": False})
            user_id = decoded_token.get("user_id")
            user = get_object_or_404(CustomUser, id=user_id)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            return Response(
                {"error": "Invalid user ID"}, status=status.HTTP_400_BAD_REQUEST
            )
        except (jwt.ExpiredSignatureError, jwt.DecodeError, jwt.InvalidTokenError):
            return Response(
                {"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST
            )

        if user.is_email_valid:
            return Response(
                {"message": "Email already verified"}, status=status.HTTP_403_FORBIDDEN
            )

        user.is_email_valid = True
        user.save()
        return Response(
            {"message": "Email verified successfully"}, status=status.HTTP_200_OK
        )


class PasswordResetRequest(APIView):
    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response(
                {"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response(
                {"error": "User with this email does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )

        token = RefreshToken.for_user(user)
        current_site = get_current_site(request).domain
        relative_link = reverse(
            "password_reset_confirm",
            kwargs={
                "token": token,
                "uidb64": urlsafe_base64_encode(force_bytes(user.id)),
            },
        )
        abs_url = "http://" + current_site + relative_link

        subject = "Password Reset Request"
        message = f"Hi {user.first_name},\n\nTo reset your password, click the link below:\n\n{abs_url}"
        sended_data = {
            "email_body": message,
            "email_subject": subject,
            "to_email": user.email,
        }
        Util.send_email(data=sended_data)

        return Response(
            {"message": "Password reset email sent"}, status=status.HTTP_200_OK
        )


class PasswordResetConfirm(APIView):
    def post(self, request, uidb64, token):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            new_password = validated_data.get("password")

            try:
                uid = urlsafe_base64_decode(uidb64).decode()
                user = CustomUser.objects.get(pk=uid)
            except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
                return Response(
                    {"error": "Invalid user ID"}, status=status.HTTP_400_BAD_REQUEST
                )

            user.set_password(new_password)
            user.save()
            return Response(
                {"message": "Password reset successfully"}, status=status.HTTP_200_OK
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    permission_classes = (IsAuthenticated,)

    def get_current_user(self, request):
        jwt_token = request.auth
        user_id = jwt_token.payload.get("id")
        user_instance = CustomUser.objects.get(id=user_id)
        return user_instance

    def get(self, request):
        user_instance = self.get_current_user(request)
        serializer = UserSerializer(user_instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        user_instance = self.get_current_user(request)
        serializer = UserSerializer(instance=user_instance, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        user_instance = self.get_current_user(request)

        if user_instance.is_investor == 1:
            return Response({"detail": "Please delete your investor profile first."},
                            status=status.HTTP_409_CONFLICT)

        if user_instance.is_startup == 1:
            return Response({"detail": "Please delete your startup profile first."},
                            status=status.HTTP_409_CONFLICT)

        user_instance.is_active = 0
        user_instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)