from django.shortcuts import get_object_or_404
from investors.models import Investor

from projects.models import Project
from projects.permissions import IsInvestor
from projects.serializers import ProjectSerializer, ProjectViewSerializer
from projects.utils import filter_projects
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from startups.models import Startup


class ProjectViewSet(viewsets.ViewSet):
    """
    ViewSet for managing project resources.

    This ViewSet provides standard CRUD operations for projects,
    including listing, retrieving, creating, updating, and deleting projects.
    Each operation corresponds to an HTTP method (GET, POST, PUT, PATCH, DELETE)
    and a URL pattern.

    Available methods:
    - list: Retrieve a list of all projects (GET /api/projects/).
    - retrieve: Retrieve information about a specific project by its ID (GET /api/projects/{id}/).
    - create: Create a new project (POST /api/projects/).
    - update: Fully update an existing project by its ID (PUT /api/projects/{id}/).
    - partial_update: Partially update an existing project by its ID (PATCH /api/projects/{id}/).
    - destroy: Delete a project by its ID (DELETE /api/projects/{id}/).

    Parameters:
    - pk: The ID of the project (used in retrieve, update, partial_update, and destroy methods).
    - request: The request object, containing request data and parameters.

    Request/Response Formats:
    - Methods accept data in JSON format and also return responses in JSON format.
    - Responses contain the status of the operation, messages, and project data (in list, retrieve, create, update, partial_update operations).
    """

    free_methods = ("list", "retrieve")
    investors_methods = ("invest_to_project")
    allowed_uqery_keys = {'project_name', 'description', 'industry', 'status', 'bgt', 'blt'}

    def get_permissions(self):
        # Configure permissions based on the action (method) that is called
        if self.action in self.free_methods:
            return []
        elif self.action in self.investors_methods:
            return [IsInvestor()]
        else:
            return [IsAuthenticated()]

    def list(self, request):
        # Implementation of GET METHOD - ExampLE URL: /api/projects/
        # Getting ALL projects logic
        queryset_projects = Project.objects.filter(is_active=True)
        query_params = request.query_params
        if query_params:
            filtered_query_data = {key: query_params[key] for key in query_params if key in self.allowed_uqery_keys}
            queryset_projects = filter_projects(queryset_projects, filtered_query_data, request)
        serializer = ProjectViewSerializer(queryset_projects, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        # Implementation of GET METHOD for one project - ExampLE URL: /api/projects/2
        # Getting ONE project with id=project logic
        project_id = pk
        try:
            project = Project.objects.get(is_active=True, id=project_id)
        except Project.DoesNotExist:
            return Response({
                'detail': f'Project with id {pk} not found.'
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = ProjectViewSerializer(project, many=False, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        """
        Create a new project (POST /api/projects/)
        Do not forget slash at the end of link
        + you should send data in JSON
        """
        user = request.user
        if not user.is_startup:
            return Response({'message': 'You\'re not a startup user'}, status=status.HTTP_400_BAD_REQUEST)
        startup = Startup.objects.filter(owner=user).first()
        if not startup:
            return Response({'message': 'Please create a startup first'}, status=status.HTTP_400_BAD_REQUEST)
        project_info = request.data
        serializer = ProjectSerializer(data=project_info)
        if serializer.is_valid():
            serializer.save(startup=startup)
            data = {
                'message': "You successfully created new project",
                'project_info': project_info,
                'status': status.HTTP_200_OK
            }
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk):
        """
        Update an existing project with all fields required
        (PUT api/projects/<pk>/)
        Do not forget about SLASH at the end of URL
        """
        try:
            project = get_object_or_404(Project, pk=pk)
            if not project.is_active:
                raise ValueError("Project is not active")
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ProjectSerializer(instance=project, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        data = {
            'project_id': pk,
            'message': f"Hello, here's a PUT method! You update ALL information about PROJECT № {pk}",
            'updated_data': request.data,
            'status': status.HTTP_200_OK
        }
        return Response(data, status=status.HTTP_200_OK)

    def partial_update(self, request, pk):
        """
        Update an existing project without all fields required
        (PATCH api/projects/<pk>/)
        Do not forget about SLASH at the end of URL
        """

        try:
            project = get_object_or_404(Project, pk=pk)
            if not project.is_active:
                raise ValueError("Project is not active")
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ProjectSerializer(instance=project, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        data = {
            'project_id': pk,
            'message': f"Hello, here's a PATCH method! You update ALL information about PROJECT № {pk}",
            'updated_data': request.data,
            'status': status.HTTP_200_OK
        }
        return Response(data, status=status.HTTP_200_OK)

    #
    # def destroy(self, request, pk=None):
    #     # Implementation of DELETE METHOD for one project - ExampLE URL: /api/projects/4/
    #     # Do not forget about SLASH at the end of URL
    #     # Deleting logic
    #     project_id = pk
    #     data = {
    #         'project_id': project_id,
    #         'message': f"Hello, you DELETED PROJECT with ID: {project_id}",
    #         'status': status.HTTP_200_OK
    #     }
    #     return Response(data, status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], url_path='my')
    def get_my_projects(self, request):
        user = self.request.user
        investors_projects = Project.objects.filter(investors__id=user.id, is_active=True)
        serializer = ProjectViewSerializer(investors_projects, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='invest')
    def invest_to_project(self, request, pk=None):
        """
        This function allows adding an investor to a project.
        The user must be authenticated and have an active investor linked to their account.
        The investor is added to the project only if the project is active and does not already contain this investor

        :param self: Allow an instance of a class to access its attributes and methods
        :param request: Get the user from the request
        :param pk: The primary key of the project.
        :return: Response: A response with a detailed message about the result of the operation.
        Examples:
        Use this method by sending a POST request to the URL: /api/projects/12/invest
        where 12 is the ID of the project you want to add an investor to.
        """
        
        try:
            user = request.user
            project = Project.objects.get(id=pk, is_active=True)
            investor = Investor.objects.get(user=user, is_active=True)
            if project.investors.filter(id=investor.id).exists():
                return Response({
                    'detail': f'Investor {user.first_name} {user.last_name} is already an investor in project {project.project_name}.'
                }, status=status.HTTP_400_BAD_REQUEST)

            project.investors.add(investor)

            return Response({
                'detail': f'Investor {user.first_name} {user.last_name} has been added to project {project.project_name}.'
            }, status=status.HTTP_200_OK)

        except Project.DoesNotExist:
            return Response({
                'detail': f'Project with id {pk} not found or inactive.'
            }, status=status.HTTP_404_NOT_FOUND)

        except Investor.DoesNotExist:
            return Response({
                'detail': f'Investor not found or inactive for user {request.user.id}.'
            }, status=status.HTTP_404_NOT_FOUND)
