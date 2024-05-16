from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from startups.models import Industry
from users.models import CustomUser


from projects.models import Project
from projects.serializers import ProjectSerializer
from users.models import CustomUser
from .models import Investor
from .serializers import InvestorSerializer


class IsInvestorPermission(permissions.BasePermission):
    """
    Custom permission to only allow investors to interact with the view.
    """

    def has_permission(self, request, view):
        return request.user.is_investor == 1 and request.user.is_authenticated


class InvestorViewSet(viewsets.ViewSet):
    def get_permissions(self):
        permission_list = ["list", "retrieve", "all_subscribed_projects", "remove_subscribed_project"]
        if self.action in permission_list:
            return []
        elif self.action == "create":
            return [IsAuthenticated()]
        return [IsInvestorPermission()]

    def list(self, request):
        investors = Investor.objects.filter(is_active=True)
        serializer = InvestorSerializer(investors, many=True)
        for data in serializer.data:
            investor = Investor.objects.get(id=data['id'])
            interests = investor.interests.all().values_list('name', flat=True)
            data['interests'] = list(interests)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        investor = get_object_or_404(Investor, id=pk, is_active=True)
        serializer = InvestorSerializer(investor)
        for data in serializer.data:
            investor = Investor.objects.get(id=data['id'])
            interests = investor.interests.all().values_list('name', flat=True)
            serializer.data['interests'] = list(interests)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        jwt_token = request.auth
        user_id = jwt_token.payload.get("id")

        existing_investor = Investor.objects.filter(user=user_id).first()
        if existing_investor:
            return Response({"error": "Investor already exists for this user"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = InvestorSerializer(data=request.data)
        if serializer.is_valid():
            user_instance = CustomUser.objects.get(id=user_id)
            user_instance.is_investor = 1
            user_instance.save()
            interests_data = serializer.validated_data.pop('interests', [])
            investor = Investor.objects.create(user=user_instance, **serializer.validated_data)
            industries = [Industry.objects.get_or_create(name=name)[0] for name in interests_data]
            investor.interests.set(industries)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        investor = get_object_or_404(Investor, id=pk)
        serializer = InvestorSerializer(instance=investor, data=request.data)
        if serializer.is_valid():
            interests_data = serializer.validated_data.pop('interests', [])
            serializer.save()
            industries = [Industry.objects.get_or_create(name=name)[0] for name in interests_data]
            investor.interests.set(industries)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        investor = get_object_or_404(Investor, id=pk)
        serializer = InvestorSerializer(
            instance=investor, data=request.data, partial=True)
        if serializer.is_valid():
            interests_data = serializer.validated_data.pop('interests', [])
            serializer.save()
            industries = [Industry.objects.get_or_create(name=name)[0] for name in interests_data]
            investor.interests.set(industries)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def destroy(self, request, pk=None):
        investor = get_object_or_404(Investor, id=pk)
        investor.is_active = 0
        user_instance = investor.user
        user_instance.is_investor = 0

        with transaction.atomic():
            investor.save()
            user_instance.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], url_path='follows')
    def all_subscribed_projects(self, request, pk=None):
        """
        Get all subscribed projects of the investor.
        This action retrieves a list of all projects that the investor is subscribed to.
        Parameters:
        - request (Request): The HTTP request object.
        - pk (int): The primary key of the investor. If provided, fetch projects subscribed by this investor.
        Returns:
        Response: A JSON response containing a list of subscribed projects.
        """
        try:
            user = request.user
            if pk is None:
                investor = get_object_or_404(Investor, pk=user.id, is_active=True)
            else:
                investor = get_object_or_404(Investor, pk=pk, is_active=True)
            subscribed_projects = investor.subscribed_projects.all()
            serializer = ProjectSerializer(subscribed_projects, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Investor.DoesNotExist:
            return Response({'error': 'Investor not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'], url_path='remove_subscribed_project')
    def remove_subscribed_project(self, request, pk=None):
        """
        Remove a project from the investor's subscribed projects.
        This action allows removing a project from the list of subscribed projects of the investor.
        It expects a POST request with the project's ID included in the request data.
        Upon successful removal, it returns a success message along with HTTP 200 OK status code.
        Parameters:
        - request (Request): The HTTP request object.
        - pk (int): The primary key of the investor.
        Returns:
        Response: A JSON response containing a success message upon successful removal of the project.
        """
        try:
            investor = Investor.objects.get(pk=pk)
            project_id = request.data.get('project_id')
            project = get_object_or_404(Project, pk=project_id)
            investor.subscribed_projects.remove(project)
            return Response({'message': f'Project {project_id} successfully removed from subscribed projects'},
                            status=status.HTTP_200_OK)
        except Investor.DoesNotExist:
            return Response({'error': 'Investor not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=["get"], url_path="profile")
    def get_my_profile(self, request):
        jwt_token = request.auth
        user_id = jwt_token.payload.get("id")
        user_instance = CustomUser.objects.get(id=user_id)

        investor = get_object_or_404(Investor, user=user_instance, is_active=True)
        serializer = InvestorSerializer(investor)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'], url_path='add-new-interests')
    def partial_interests_update(self, request, pk=None):
        investor = get_object_or_404(Investor, id=pk)
        new_interests = request.data.get('interests', [])
        if not isinstance(new_interests, list):
            return Response(
                {"detail": "Interests should be a list of industry names."}, status=status.HTTP_400_BAD_REQUEST)
        for interest_name in new_interests:
            try:
                industry = Industry.objects.get(name=interest_name)
                if industry not in investor.interests.all():
                    investor.interests.add(industry)
            except Industry.DoesNotExist:
                return Response(
                    {"detail": f"Industry '{interest_name}' does not exist."}, status=status.HTTP_400_BAD_REQUEST)

        investor.save()
        serializer = InvestorSerializer(investor)
        return Response(serializer.data, status=status.HTTP_200_OK)

