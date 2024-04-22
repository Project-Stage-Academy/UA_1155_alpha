# views.py
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

import users
from users.models import CustomUser
from django.http import JsonResponse

from users.utils import Util


class PasswordRecoveryRequest(APIView):
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User with this email does not exist'}, status=status.HTTP_404_NOT_FOUND)

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        reset_url = '/reset-password'

        subject = 'Password Reset Request'
        message = f'Hi {user.first_name},\n\nTo reset your password, click the link below:\n\n{reset_url}'
        sended_data = {'email_body': message, 'email_subject': subject, 'to_email': user.email}
        Util.send_email(data=sended_data)

        return Response({'message': 'Password reset email sent'}, status=status.HTTP_200_OK)


class PasswordResetConfirm(APIView):
    def post(self, request, uidb64, token):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            new_password = request.data.get('new_password')
            if not new_password:
                return Response({'error': 'New password is required'}, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(new_password)
            user.save()
            return Response({'message': 'Password reset successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid password reset link'}, status=status.HTTP_400_BAD_REQUEST)


def simple_json_view_users(request):
    data = {
        'message': 'Hello, USER PAGE',
        'status': 'success'
    }
    return JsonResponse(data)
