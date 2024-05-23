from rest_framework import status
from rest_framework.test import force_authenticate, APIRequestFactory
from django.test import TestCase
from mixer.backend.django import mixer

from users.models import CustomUser
from startups.models import Startup, Industry
from startups.views import StartupViewSet
from projects.models import Project


class IndustryModelTestCase(TestCase):
    def setUp(self):
        Industry.objects.all().delete()

    def tearDown(self):
        try:
            Startup.objects.all().delete()
            Industry.objects.all().delete()
        except Exception as e:
            print("Error during cleanup:", e)

    def test_industry_creation(self):
        industry = mixer.blend(Industry, name="Technology")
        self.assertEqual(str(industry), "Technology")
        self.assertTrue(isinstance(industry, Industry))

    def test_unique_industry_name(self):
        name = "Technology"
        Industry.objects.create(name=name)
        with self.assertRaises(Exception):
            Industry.objects.create(name=name)


class StartupViewSetTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = StartupViewSet.as_view({'get': 'list', 'post': 'create', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'})
        self.user = mixer.blend(CustomUser, is_startup=True)
        self.user.save()
        self.industry = mixer.blend(Industry, name='Health Care')
        self.industry.save()
        self.startup = mixer.blend(Startup, owner=self.user, industries=self.industry)
        self.startup.save()
        self.url = '/api/startups/'
        self.partial_data = {
            'description': 'Updated Description',
            'industries': 'Health Care'
        }
        self.data = {
            'startup_name': 'My new startup',
            'description': 'This is the description of my startup',
            'industries': 'Health Care',
            'location': 'Yellowstone-National Park',
            'contact_phone': '+31234567899',
            'contact_email': 'info@2example.com',
            'number_for_startup_validation': 12345671,
            'is_verified': True,
            'is_active': True,
        }

    def test_create_startup_success(self):
        '''
        Test for positive case of creating a startup
        '''
        existing_startup = Startup.objects.filter(owner=self.user).first()
        if existing_startup:
            existing_startup.delete()

        request = self.factory.post(self.url, self.data, format='json')
        force_authenticate(request, user=self.user)
        response = self.view(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Startup.objects.filter(owner=self.user).exists())

    def test_create_startup_existing_user(self):
        '''
        Test for negative case of creating a startup for user with an existing startup
        '''
        mixer.blend(Startup, owner=self.user, industries=self.industry)
        request = self.factory.post(self.url, self.data, format='json')
        force_authenticate(request, user=self.user)
        response = self.view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], "Startup already exists for this user")

    def test_invalid_contact_email(self):
        """
          Invalid contact email test.
          """
        new_user = mixer.blend(CustomUser, is_startup=True)
        invalid_data = self.data.copy()
        invalid_data['contact_email'] = 'invalid_email'
        request = self.factory.post(self.url, invalid_data, format='json')
        force_authenticate(request, user=new_user)
        response = self.view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(isinstance(response.data, dict))
        self.assertIn('contact_email', response.data)

    def test_invalid_contact_phone(self):
        """
        Invalid contact phone number test.
        """
        new_user = mixer.blend(CustomUser, is_startup=True)
        invalid_data = self.data.copy()
        invalid_data['contact_phone'] = 'invalid_phone_number'
        request = self.factory.post(self.url, invalid_data, format='json')
        force_authenticate(request, user=new_user)
        response = self.view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(isinstance(response.data, dict))
        self.assertIn('Error', response.data)

    def test_invalid_startup_validation_number(self):
        """
        Test for invalid startup validation number.
        """
        new_user = mixer.blend(CustomUser, is_startup=True)
        invalid_data = self.data.copy()
        invalid_data['number_for_startup_validation'] = 'invalid_number'
        request = self.factory.post(self.url, invalid_data, format='json')
        force_authenticate(request, user=new_user)
        response = self.view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(isinstance(response.data, dict))
        self.assertIn('number_for_startup_validation', response.data)

    def test_update_startup_success(self):
        '''
        Test for positive case of updating a startup
        '''
        request = self.factory.put(f'{self.url}{self.startup.id}/', self.data, format='json')
        force_authenticate(request, user=self.user)
        response = self.view(request, pk=self.startup.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Startup.objects.get(pk=self.startup.id).description, self.data['description'])

    def test_update_not_authorized(self):
        '''
        Test for negative case of updating a startup by not-authorized user
        '''
        request = self.factory.put(f'{self.url}{self.startup.id}/', self.data, format='json')
        response = self.view(request, pk=self.startup.id)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_startup_not_exist(self):
        '''
        Test for negative case of updating a non-existing startup
        '''
        request = self.factory.put(f'{self.url}{self.startup.id}/', self.data, format='json')
        force_authenticate(request, user=self.user)
        response = self.view(request, pk=self.startup.id + 1)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_partial_update_startup_success(self):
        '''
        Test for positive case of partially updating a startup
        '''
        self.partial_data = {
            'contact_phone': '+380501234567'
        }
        request = self.factory.patch(f'{self.url}{self.startup.id}/', self.partial_data, format='json')
        force_authenticate(request, user=self.user)
        response = self.view(request, pk=self.startup.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Startup.objects.get(pk=self.startup.id).contact_phone, self.partial_data['contact_phone'])

    def test_partial_update_not_authorized(self):
        '''
        Test for negative case of partially updating a startup by not-authorized user
        '''
        request = self.factory.patch(f'{self.url}{self.startup.id}/', self.partial_data, format='json')
        response = self.view(request, pk=self.startup.id)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_partial_update_startup_not_exist(self):
        '''
        Test for negative case of partially updating a non-existing startup
        '''
        request = self.factory.patch(f'{self.url}{self.startup.id}/', self.partial_data, format='json')
        force_authenticate(request, user=self.user)
        response = self.view(request, pk=self.startup.id + 1)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_partial_update_startup_wrong_industry(self):
        '''
        Test for negative case of partially updating a startup with a wrong industry
        '''
        self.partial_data = {
            'industries': 'Wrong Industry'
        }
        request = self.factory.patch(f'{self.url}{self.startup.id}/', self.partial_data, format='json')
        force_authenticate(request, user=self.user)
        response = self.view(request, pk=self.startup.id)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_destroy_startup_success(self):
        '''
        Test for positive case of deleting a startup
        '''
        request = self.factory.delete(f'{self.url}{self.startup.id}/')
        force_authenticate(request, user=self.user)
        response = self.view(request, pk=self.startup.id)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Startup.objects.get(pk=self.startup.id).is_active)

    def test_destroy_not_authorized(self):
        '''
        Test for negative case of deleting a startup by not-authorized user
        '''
        request = self.factory.delete(f'{self.url}{self.startup.id}/')
        response = self.view(request, pk=self.startup.id)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_destroy_startup_not_exist(self):
        '''
        Test for negative case of deleting a non-existing startup
        '''
        request = self.factory.delete(f'{self.url}{self.startup.id + 1}/')
        force_authenticate(request, user=self.user)
        response = self.view(request, pk=self.startup.id + 1)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_destroy_startup_with_active_projects(self):
        '''
        Test for the case of deleting a startup with active projects
        '''
        request = self.factory.delete(f'{self.url}{self.startup.id}/')
        force_authenticate(request, user=self.user)
        projects_exist = Project.objects.filter(startup=self.startup, is_active=True).exists()
        response = self.view(request, pk=self.startup.id)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT if projects_exist else status.HTTP_204_NO_CONTENT)
        startup = Startup.objects.get(pk=self.startup.id)
        self.assertTrue(startup.is_active) if projects_exist else self.assertFalse(startup.is_active)





