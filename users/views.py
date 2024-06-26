import jwt
from django.contrib.sites.shortcuts import get_current_site
from django.db.models.functions import Now
from django.urls import reverse
from drf_yasg.utils import swagger_auto_schema
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
from .swagger_auto_schema_settings import *
from .utils import Util


class LoginAPIView(APIView):
    """
    Endpoint for user login.
    This endpoint allows users to login by providing their email and password.
    Parameters:
    - `request`: HTTP request object.
    Returns:
    - 200: Successful login. Returns the refresh and access tokens.
    - 400: Bad request. Returns a message indicating that the user was not found.
    - 401: Unauthorized. Returns a message indicating that the password is incorrect.
    Example request data:
    {
        "email": "john@example.com",
        "password": "strongPassword123!"
    }
    Example successful response:
    HTTP 200 OK
    {
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
    Example error response (user not found):
    HTTP 400 Bad Request
    {
        "message": "User not found"
    }
    Example error response (wrong password):
    HTTP 401 Unauthorized
    {
        "message": "Wrong password"
    }
    """

    @swagger_auto_schema(
        security=[],
        tags=["USER REGISTER, LOG_IN, LOG-OUT"],
        request_body=loginAPIView_body,
        responses=loginAPIView_responses,
    )
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
    """
    Endpoint for logging out a user by invalidating their refresh token.
    This endpoint expects a POST request with the "access" and "refresh" tokens provided in the request body.
    Parameters:
    - `request`: HTTP request object containing the refresh token to be invalidated.
    Returns:
    - 200: Successful exit. Returns a success message if the refresh token was successfully invalidated.
    - 400: Bad request. Returns an error message if the refresh token is missing or invalid.
    Example request data:
    {
        "refresh": "your_refresh_token_here"
    }
    Example successful response:
    HTTP 200 OK
    {
        "success": "Successful exit"
    }
    Example error response:
    HTTP 400 Bad Request
    {
        "error": "Refresh token is required."
    }
    """

    @swagger_auto_schema(
        tags=["USER REGISTER, LOG_IN, LOG-OUT"],
        request_body=logoutAPIView_body,
        responses=logoutAPIView_responses,
    )
    def post(self, request):
        """Method should receive "refresh" tokens in body of POST request to LogOut"""
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
    """
    Endpoint for registering a new user.
    This endpoint allows users to register by providing their first name, last name, email, password, and confirming the password.
    Parameters:
    - `request`: HTTP request object.
    Returns:
    - 201: User created successfully. Returns the user's first name and a success message.
    - 400: Bad request. Returns validation errors if the request data is invalid.
    - 500: Internal Server Error. Returns an error message if there was an issue creating the user.

    Example request data:
    {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "password": "strongPassword123!",
        "password2": "strongPassword123!"
    }
    Example successful response:
    HTTP 201 Created
    {
        "User name": "John",
        "message": "User created successfully"
    }
    Example error response:
    HTTP 400 Bad Request
    {"email": ["Enter a valid email address."]}
    """

    @swagger_auto_schema(
        security=[],
        tags=["USER REGISTER, LOG_IN, LOG-OUT"],
        request_body=userRegisterAPIView_body,
        responses=userRegisterAPIView_responses,
    )
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
    """
    API endpoint for confirming the user's email address.
    This endpoint provides functionality to confirm a user's email address using a token.
    Parameters:
    - `request`: HTTP request object.
    - `token`: The confirmation token sent to the user's email.
    Returns:
    - 200: OK. Returns a message indicating that the email confirmation is required.
    - 400: Bad Request. Returns an error message if the token is missing or invalid.
    - 403: Forbidden. Returns a message indicating that the email has already been verified.

    Example successful GET response:
    HTTP 200 OK
    {"message": "Plese, confifm your email"}
    Example successful POST response:
    {"message": "Email verified successfully"}

    Example request data:
    - In GET request: A valid token is required in the request header.
    - In POST request: A valid token is required in the request header.

    Example error response:
    HTTP 400 Bad Request
    {"error": "Invalid token"}
    """

    @swagger_auto_schema(
        tags=["USER REGISTER, LOG_IN, LOG-OUT"],
        responses=sendEmailConfirmationAPIView_responses_GET,
    )
    def get(self, request, token=None):
        return Response(
            {"message": "Plese, confifm your email"}, status=status.HTTP_200_OK
        )

    @swagger_auto_schema(
        tags=["USER REGISTER, LOG_IN, LOG-OUT"],
        responses=sendEmailConfirmationAPIView_responses_POST,
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
    """
    API endpoint for requesting a password reset.
    This endpoint allows users to request a password reset by providing their email address.
    Parameters:
    - `request`: HTTP request object containing the user's email address.
    Returns:
    - 200: OK. Returns a message indicating that the password reset email has been sent successfully.
    - 400: Bad Request. Returns an error message if the email is missing.
    - 404: Not Found. Returns an error message if no user is found with the provided email address.

    Example request data:
    {"email": "user@example.com"}

    Example successful response:
    HTTP 200 OK
    {"message": "Password reset email sent"}

    Example error response:
    HTTP 400 Bad Request
    {"error": "Email is required"}
    """

    @swagger_auto_schema(
        tags=["RESET PASSWORD"],
        request_body=passwordResetRequest_body,
        responses=passwordResetRequest_responses,
    )
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
    """
    API endpoint for confirming a password reset.
    This endpoint allows users to confirm a password reset by providing a new password along with the token
    received in the password reset email.
    Parameters:
    - `request`: HTTP request object containing the new password.
    - `token`: Token received in the password reset email.
    Returns:
    - 200: OK. Returns a message indicating that the password has been reset successfully.
    - 400: Bad Request. Returns an error message if the provided data is invalid or if the token is invalid.

    Example request data:
    {"password": "new_password_here"}

    Example successful response:
    HTTP 200 OK
    {"message": "Password reset successfully"}

    Example error response:
    HTTP 400 Bad Request
    {"password": ["This field is required."]}
    """

    @swagger_auto_schema(
        tags=["RESET PASSWORD"],
        request_body=PasswordResetConfirmSerializer,
        responses=passwordResetConfirm_responses,
    )
    def post(self, request, token):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            new_password = validated_data.get("password")

            try:
                decoded_token = jwt.decode(token, options={"verify_signature": False})
                user_id = decoded_token.get("user_id")
                user = get_object_or_404(CustomUser, id=user_id)
            except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
                return Response(
                    {"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST
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
        serializer = UserSerializer(instance=user_instance, data=request.data, partial=True)

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