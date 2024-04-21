# views.py
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from datetime import datetime, timedelta


# class PasswordRecoveryRequest(APIView):
#     def post(self, request):
#         email = request.data.get('email')
#         if not email:
#             return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
#
#         try:
#             user = User.objects.get(email=email)
#         except User.DoesNotExist:
#             return Response({'error': 'User with this email does not exist'}, status=status.HTTP_404_NOT_FOUND)
#
#         # Generate password reset token
#         uid = urlsafe_base64_encode(force_bytes(user.pk))
#         token = default_token_generator.make_token(user)
#
#         # Construct password reset link
#         reset_url = settings.FRONTEND_URL + reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
#
#         # Send password reset email
#         subject = 'Password Reset Request'
#         message = f'Hi {user.username},\n\nTo reset your password, click the link below:\n\n{reset_url}'
#         send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
#
#         return Response({'message': 'Password reset email sent'}, status=status.HTTP_200_OK)
#
#
# class PasswordResetConfirm(APIView):
#     def post(self, request, uidb64, token):
#         try:
#             uid = force_text(urlsafe_base64_decode(uidb64))
#             user = User.objects.get(pk=uid)
#         except (TypeError, ValueError, OverflowError, User.DoesNotExist):
#             user = None
#
#         if user is not None and default_token_generator.check_token(user, token):
#             new_password = request.data.get('new_password')
#             if not new_password:
#                 return Response({'error': 'New password is required'}, status=status.HTTP_400_BAD_REQUEST)
#
#             # Add your password complexity validation here
#
#             user.set_password(new_password)
#             user.save()
#             return Response({'message': 'Password reset successfully'}, status=status.HTTP_200_OK)
#         else:
#             return Response({'error': 'Invalid password reset link'}, status=status.HTTP_400_BAD_REQUEST)
#

def simple_json_view_users(request):
    data = {
        'message': 'Hello, USER PAGE',
        'status': 'success'
    }
    return JsonResponse(data)
