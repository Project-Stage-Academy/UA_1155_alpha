from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework import status
from .views import ProjectViewSet
from projects.models import Project
from users.models import CustomUser
from investors.models import Investor
from startups.models import Startup, Industry
from mixer.backend.django import mixer


class ProjectViewSetTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = ProjectViewSet.as_view({'get': 'list', 'post': 'create', 'put': 'update', 'patch': 'partial_update'})
        self.user = mixer.blend(CustomUser)
        self.user.save()
        self.industry = mixer.blend(Industry, name='Testik')
        self.industry.save()
        self.startup = mixer.blend(Startup, owner=self.user, industries=self.industry)
        self.startup.save()
        self.project = mixer.blend(Project, startup=self.startup, is_active = True)
        self.project.save()
        self.investor = mixer.blend(Investor, user=self.user)
        self.url = '/api/projects/'
        self.partial_data = {'description': 'Updated Description', 'industry': 'Testik'}
        self.data = {
                'startup': self.startup.id,
                'project_name': 'Назва вашого проекту',
                'description': 'Опис вашого проекту',
                'goals': 'Мети вашого проекту',
                'budget_needed': 10000.0,
                'budget_ready': 5000.0,
                'industry': 'Testik',
                'promo_photo_url': 'URL фотографії для просування',
                'promo_video_url': 'URL відео для просування',
                'status': 'pending',
                'rating': 4.5,
                'is_active': True,
        }

        
    def test_update_project_success(self):
        '''
        Test for positive case of working PUT method in Project
        '''
        request = self.factory.put(f'{self.url}{self.project.id}/', self.data, format='json')
        force_authenticate(request, user=self.user)
        response = self.view(request, pk=self.project.id)
        self.assertEqual(Project.objects.get(pk=self.project.id).description, self.data['description'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_update_not_authorized(self):
        '''
        Test for negative case of working PUT method in Project because of not-authorized user
        '''
        request = self.factory.put(f'{self.url}{self.project.id}/', self.data, format='json')
        response = self.view(request, pk=self.project.id)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_update_project_not_exist(self):
        '''
        Test for negative case of working PUT method in Project because of not existing project
        '''
        request = self.factory.put(f'{self.url}{self.project.id}/', self.data, format='json')
        force_authenticate(request, user=self.user)
        response = self.view(request, pk=self.project.id+1)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_update_project_not_active(self):
        '''
        Test for negative case of working PUT method in Project because of not active project
        '''
        self.data['is_active'] = None
        request = self.factory.put(f'{self.url}{self.project.id}/', self.data, format='json')
        force_authenticate(request, user=self.user)
        response = self.view(request, pk=self.project.id)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_update_project_wrong_industry(self):
        '''
        Test for negative case of working PUT method in Project because of wrong industry
        '''
        self.data['industry'] = 'Wrong industry'
        request = self.factory.put(f'{self.url}{self.project.id}/', self.data, format='json')
        force_authenticate(request, user=self.user)
        response = self.view(request, pk=self.project.id)
        self.assertEqual(response.data.get('error'), 'Industry does not exist')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_update_project_none_industry(self):
        '''
        Test for negative case of working PUT method in Project because of none industry
        '''
        self.data['industry'] = None
        request = self.factory.put(f'{self.url}{self.project.id}/', self.data, format='json')
        force_authenticate(request, user=self.user)
        response = self.view(request, pk=self.project.id)
        self.assertEqual(response.data.get('error'), 'Please provide industry')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)



    def test_partial_update_project_seccess(self):
        '''
        Test for positive case of working PATCH method in Project
        '''
        data = {'description': 'Updated Description', 'industry': 'Testik'}
        request = self.factory.patch(f'{self.url}{self.project.id}/', self.partial_data, format='json')
        force_authenticate(request, user=self.user)
        response = self.view(request, pk=self.project.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_partial_update_not_authorized(self):
        '''
        Test for negative case of working PATCH method in Project because of not-authorized user
        '''
        request = self.factory.patch(f'{self.url}{self.project.id}/', self.partial_data, format='json')
        response = self.view(request, pk=self.project.id)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_partial_update_project_not_exist(self):
        '''
        Test for negative case of working PATCH method in Project because of not existing project
        '''
        request = self.factory.patch(f'{self.url}{self.project.id}/', self.partial_data, format='json')
        force_authenticate(request, user=self.user)
        response = self.view(request, pk=self.project.id+1)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_partial_update_project_not_active(self):
        '''
        Test for negative case of working PATCH method in Project because of not active project
        '''
        self.partial_data['is_active'] = None
        print(self.data)
        request = self.factory.patch(f'{self.url}{self.project.id}/', self.partial_data, format='json')
        force_authenticate(request, user=self.user)
        response = self.view(request, pk=self.project.id)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_partial_update_project_wrong_industry(self):
        '''
        Test for negative case of working PATCH method in Project because of wrong industry
        '''
        self.partial_data['industry'] = 'Wrong industry for test'
        request = self.factory.patch(f'{self.url}{self.project.id}/', self.partial_data, format='json')
        force_authenticate(request, user=self.user)
        response = self.view(request, pk=self.project.id)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_partial_update_project_none_industry(self):
        '''
        Test for negative case of working PATCH method in Project because of none industry
        '''
        self.partial_data['industry'] = None
        request = self.factory.patch(f'{self.url}{self.project.id}/', self.partial_data, format='json')
        force_authenticate(request, user=self.user)
        response = self.view(request, pk=self.project.id)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)