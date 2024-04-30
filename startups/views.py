from rest_framework import status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Startup
from .serializers import StartupListSerializer, StartupSerializer
from .view import filter_queryset_by_params as filter_startups, list as list_startups


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
    permission_classes = (IsAuthenticated,)

    def list(self, request):
        # Example URL: /api/startups/
        # Getting ALL startups logic
        return list_startups(self, request)

    def filter_queryset_by_params(self, queryset, query_params):
        # Example URL: /api/startups/?industry=test
        # Example URL: /api/startups/?name=test
        return filter_startups(self, queryset, query_params)

    def retrieve(self, request, pk=None):
        # ExampLE URL: /api/startups/2
        # Getting ONE startup with id=startup_id logic
        try:
            startup = get_object_or_404(Startup, id=pk)
            if not startup.is_active:
                return Response({"error": "Startup not active"}, status=status.HTTP_400_BAD_REQUEST)
            serializer = StartupListSerializer(startup)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response({"error": "Invalid startup id"}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        # ExampLE URL: /api/startups/
        # Creating startup logic
        existing_startup = Startup.objects.filter(owner=request.user).first()
        if existing_startup:
            return Response({"error": "Startup already exists for this user"}, status=status.HTTP_400_BAD_REQUEST)
        startup_info = request.data
        serializer = StartupSerializer(data=startup_info, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        # ExampLE URL: /api/startups/2/
        # PUT logic
        try:
            startup = get_object_or_404(Startup, id=pk)
            serializer = StartupSerializer(startup, data=request.data, partial=False)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            if not startup.is_active:
                raise ValidationError({"error": "Startup not active"})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


    def partial_update(self, request, pk=None):
        # ExampLE URL: /api/startups/2/
        # Update info about startup
        try:
            startup = get_object_or_404(Startup, id=pk)
            serializer = StartupSerializer(startup, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            if not startup.is_active:
                raise ValidationError({"error": "Startup not active"})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

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
