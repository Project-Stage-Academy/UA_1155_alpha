from django.shortcuts import get_object_or_404

from projects.models import Project
from projects.serializers import ProjectSerializer, ProjectSerializerUpdate
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from startups.models import Startup
from notifications.tasks import project_updating


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
    permission_classes = (IsAuthenticated,)

    # def list(self, request):
    #     # Implementation of GET METHOD - ExampLE URL: /api/projects/
    #     # Getting ALL projects logic
    #
    #     data = {
    #         'message': "Hello, ALL Projects PROFILE PAGE",
    #         'status': status.HTTP_200_OK,
    #     }
    #     query_data = get_query_dict(request)  # If we need to use queries like /api/projects?name=Project1
    #     if query_data:
    #         data.update(query_data)
    #
    #     # Should return a list!
    #     return Response(data, status=status.HTTP_200_OK)
    #
    # def retrieve(self, request, pk=None):
    #     # Implementation of GET METHOD for one project - ExampLE URL: /api/projects/2
    #     # Getting ONE project with id=project logic
    #
    #     project_id = pk
    #     data = {
    #         'project_id': project_id,
    #         'message': f"Hello, concrete PROJECT profile page with id {project_id}",
    #         'status': status.HTTP_200_OK
    #     }
    #     query_data = get_query_dict(request)
    #     if query_data:
    #         data.update(query_data)
    #
    #     return Response(data, status=status.HTTP_200_OK)

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
        serializer.save()

        current_site = get_current_site(request).domain
        for investor in project.subscribers.all():
            project_updating.delay(investor.id, project.id, current_site)


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
