from django.contrib.sites.shortcuts import get_current_site
from django.http import JsonResponse
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import CustomUser
from users.serializers import PasswordResetConfirmSerializer
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


def simple_json_view_users(request):
    data = {
        'message': 'Hello, USER PAGE',
        'status': 'success'
    }
    return JsonResponse(data)
