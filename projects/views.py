from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from investors.models import Investor
from projects.models import Project
from projects.serializers import ProjectSerializerUpdate, ProjectSerializer, ProjectViewSerializer
from projects.permissions import IsInvestor
from projects.utils import filter_projects, calculate_difference
from startups.models import Startup, Industry
from notifications.signals import project_updated_signal, project_subscription_signal


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

    free_methods = ("list", "retrieve", "compare_projects")
    investors_methods = ("invest_to_project", "get_my_projects", "add_subscriber")
    allowed_uqery_keys = ('project_name', 'description', 'industry', 'status', 'bgt', 'blt')

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
            project = get_object_or_404(Project, is_active=True, id=project_id)
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
        industry_name = request.data.get('industry')
        industry = get_object_or_404(Industry, name=industry_name)
        project_info = request.data
        project_info['industry'] = industry.id
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
        industry_name = request.data.get('industry')
        if industry_name:
            try:
                industry = Industry.objects.get(name=industry_name)
            except Industry.DoesNotExist:
                return Response({"error": "Industry does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            industry = project.industry
        serializer = ProjectSerializerUpdate(instance=project, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        if industry is not None:
            serializer.validated_data['industry'] = industry
        else:
            return Response({"error": "Please provide industry"}, status=status.HTTP_400_BAD_REQUEST)
        serializer.validated_data['is_verified'] = False
        serializer.save()

        for investor in project.subscribers.all():
            project_updated_signal.send(sender=Project, investor_id=investor.id, project_id=project.id)

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
        industry_name = request.data.get('industry')
        if industry_name:
            try:
                industry = Industry.objects.get(name=industry_name)
            except Industry.DoesNotExist:
                return Response({"error": "Industry does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            industry = project.industry
        serializer = ProjectSerializerUpdate(instance=project, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        if industry is not None:
            serializer.validated_data['industry'] = industry
        else:
            return Response({"error": "Please provide industry"}, status=status.HTTP_400_BAD_REQUEST)
        serializer.validated_data['is_verified'] = False
        serializer.save()

        for investor in project.subscribers.all():
            project_updated_signal.send(sender=Project, investor_id=investor.id, project_id=project.id)

        data = {
            'project_id': pk,
            'message': f"Hello, here's a PATCH method! You update ALL information about PROJECT № {pk}",
            'updated_data': request.data,
            'status': status.HTTP_200_OK
        }
        return Response(data, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        # Implementation of DELETE METHOD for one project - ExampLE URL: /api/projects/4/
        # Do not forget about SLASH at the end of URL
        # Deleting logic
        project = get_object_or_404(Project, id=pk)
        project.is_active = 0
        project.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

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

        user = request.user
        project = get_object_or_404(Project, is_active=True, id=pk)
        investor = get_object_or_404(Investor, user=user, is_active=True)

        if project.investors.filter(id=investor.id).exists():
            return Response({
                'detail': f'Investor {user.first_name} {user.last_name} is already an investor in project {project.project_name}.'
            }, status=status.HTTP_400_BAD_REQUEST)

        project.investors.add(investor)

        return Response({
            'detail': f'Investor {user.first_name} {user.last_name} has been added to project {project.project_name}.'
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='add_subscriber')
    def add_subscriber(self, request, pk=None):
        """
        Add a subscriber to the project.
        This action allows adding a subscriber to the specified project. It expects a POST request with the subscriber's
        ID included in the request data. Upon successful addition, it returns a success message along with
        HTTP 200 OK status code.
        Parameters:
        - request (Request): The HTTP request object.
        - pk (int): The primary key of the project to which the subscriber will be added.
        Returns:
        Response: A JSON response containing a success message upon successful addition of the subscriber.
        Raises:
        Http404: If the specified project does not exist.
        """
        try:
            user = request.user
            project = get_object_or_404(Project, is_active=True, id=pk)
            subscriber = get_object_or_404(Investor, user=user, is_active=True)

            if project.subscribers.filter(id=subscriber.id).exists():
                project.subscribers.remove(subscriber)
                return Response({
                    'detail': f'Investor {user.first_name} {user.last_name} successfully unsubscribed from the project '
                              f'{project.project_name}.'}, status=status.HTTP_400_BAD_REQUEST)

            project.subscribers.add(subscriber)

            project_subscription_signal.send(sender=Project, project_id=project.id, subscriber_id=subscriber.id)

            return Response({'message': f'Investor {user.first_name} {user.last_name} successfully subscribed to '
                                        f'the project {project.project_name}'}, status=status.HTTP_200_OK)
        except Project.DoesNotExist:
            return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'], url_path='compare_projects')
    def compare_projects(self, request):
        try:
            project_ids = request.data.get('project_ids', [])
            projects = Project.objects.filter(pk__in=project_ids)

            if len(project_ids) < 2:
                return Response({'error': 'At least two projects are required for comparison'},
                                status=status.HTTP_400_BAD_REQUEST)

            differences = {}
            for i in range(len(projects)):
                for j in range(i + 1, len(projects)):
                    project1 = projects[i]
                    project2 = projects[j]
                    key = f'comparison_{i + 1}_{j + 1}'
                    differences[key] = calculate_difference(project1, project2)

            return Response(differences, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
