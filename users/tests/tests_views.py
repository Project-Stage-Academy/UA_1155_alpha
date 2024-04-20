from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model


User = get_user_model()


class UserAPITestCase(APITestCase):
    def test_user_information_api_view_requires_authentication(self):
        url = reverse('users:user_information')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 403)
        
    def test_send_email_confirmation_api_view_requires_authentication(self):
        url = reverse('users:send_email_confirmation')
        response = self.client.post(url)
        self.assertEquals(response.status_code, 403)
        
    def test_send_email_confirmation_api_view_creates_token(self):
        user = User.objects.create()