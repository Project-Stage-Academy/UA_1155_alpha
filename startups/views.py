from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import ProjectSerializer
from rest_framework.response import Response
from .models import Startup, Project
from forum.utils import get_query_dict
from rest_framework import viewsets


class StartupViewSet(viewsets.ViewSet):
    """
     ViewSet for managing startup resources.

     This ViewSet provides standard CRUD operations for startups,
     such as creating, retrieving a list, retrieving information about one startup,
     updating, and deleting startups. Each operation is tied to the corresponding
     HTTP method (GET, POST, PUT, PATCH, DELETE) and URL pattern.

     Available methods:
     - list: Retrieve a list of all startups (GET /api/startups/).
     - retrieve: Retrieve information about one startup by its ID (GET /api/startups/{id}/).
     - create: Create a new startup (POST /api/startups/).
     - update: Fully update an existing startup by its ID (PUT /api/startups/{id}/).
     - partial_update: Partially update an existing startup by its ID (PATCH /api/startups/{id}/).
     - destroy: Delete a startup by its ID (DELETE /api/startups/{id}/).

     Parameters:
     - pk: The ID of the startup (used in retrieve, update, partial_update, and destroy methods).
     - request: The request object, containing request data and parameters.

     Request/Response Formats:
     - Methods accept data in JSON format and also return responses in JSON format.
     - Responses contain the status of the operation, messages, and startup data (in list, retrieve, create, update, partial_update operations).
     """

    def list(self, request):
        # Implementation of GET METHOD - ExampLE URL: /api/startups/
        # Getting ALL startups logic
        data = {
            'message': "Hello, ALL STARTUPS PROFILE PAGE",
            'status': status.HTTP_200_OK
        }
        query_data = get_query_dict(request)  # If we need to use queries like /api/startups?name=Apple
        if query_data:
            data.update(query_data)
        # Should return a list!
        return Response(data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        # Implementation of GET METHOD for one startup - ExampLE URL: /api/startups/2
        # Getting ONE startup with id=startup_id logic

        startup_id = pk
        data = {
            'startup_id': startup_id,
            'message': f"Hello, concrete STARTUP PROFILE PAGE WITH NUMBER {startup_id}",
            'status': status.HTTP_200_OK
        }

        query_data = get_query_dict(request)  # If we need to use queries like /api/startups?name=AppleTV
        if query_data:
            data.update(query_data)
        return Response(data, status=status.HTTP_200_OK)

    def create(self, request):
        # Implementation of POST METHOD for one startup - ExampLE URL: /api/startups/
        # Do not forget slash at the end of link
        # + you should send data in JSON
        # Creating startup logic
        startup_info = request.data
        data = {
            'startup_info': startup_info,
            'status': 'success'
        }
        return Response(data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        # Implementation of PUT METHOD for one startup - ExampLE URL: /api/startups/2/
        # Do not forget about SLASH at the end of URL
        # + you should send data in JSON
        # PUT logic
        startup_id = pk
        startup_updated_info = request.data
        data = {
            'startup_id': startup_id,
            'message': f"Hello, EDIT STARTUP PROFILE WITH NUMBER {startup_id}",
            'updated_data': startup_updated_info,
            'status': 'success'
        }
        return Response(data)

    def partial_update(self, request, pk=None):
        # Implementation of PATCH METHOD for one startup - ExampLE URL: /api/startups/2/
        # Do not forget about SLASH at the end of URL
        # + you should send data in JSON
        # Pathcing logic
        startup_id = pk
        startup_specific_updated_info = request.data
        data = {
            'startup_id': startup_id,
            'message': f"Hello, EDIT STARTUP PROFILE WITH NUMBER {startup_id}",
            'specific_updated_data': startup_specific_updated_info,
            'status': 'success'
        }
        return Response(data)

    def destroy(self, request, pk=None):
        # Implementation of DELETE METHOD for one startup - ExampLE URL: /api/startups/4/
        # Do not forget about SLASH at the end of URL
        # Deleting logic
        startup_id = pk
        data = {
            'startup_id': startup_id,
            'message': f"Hello, YOU DELETED Startup with ID: {startup_id}",
            'status': 'success'
        }
        return Response(data)

    # Maybe we will delete this but i'd like to whow you how it works :)
    def custom_method(self, request):
        data = {
            'message': "Hello, this is custom GET method! We can use it for rendering pages",
            'status': 'success'
        }
        return Response(data)


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

    def update(self, request, pk=None):
        """
        Update an existing project with all fields required
        (PUT api/projects/<pk>/)
        Do not forget about SLASH at the end of URL
        """
        if not pk:
            return Response({"error": "Method PUT not allowed"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            instance = Project.objects.get(pk=pk)
        except:
            return Response({"error": "Project does not exist"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ProjectSerializer(instance=instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        data = {
            'project_id': pk,
            'message': f"Hello, here's a PUT method! You update ALL information about PROJECT № {pk}",
            'updated_data': request.data,
            'status': status.HTTP_200_OK
        }
        return Response(data, status=status.HTTP_200_OK)

    def partial_update(self, request, pk=None):
        """
        Update an existing project without all fields required
        (PATCH api/projects/<pk>/)
        Do not forget about SLASH at the end of URL
        """
        if not pk:
            return Response({"error": "Method PATCH not allowed"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            instance = Project.objects.get(pk=pk)
        except:
            return Response({"error": "Project does not exist"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ProjectSerializer(instance=instance, data=request.data, partial=True)
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
