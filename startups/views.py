from rest_framework import status, viewsets
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Startup, Industry
from .serializers import StartupListSerializer, StartupSerializer, StartupSerializerUpdate


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
        startups = Startup.objects.filter(is_active=True)
        filter_queryset_by_params_response = self.filter_queryset_by_params(startups, request.query_params)
        filtered_startups = filter_queryset_by_params_response['queryset']
        if filter_queryset_by_params_response['status'] == 'error':
            return Response({"error": filter_queryset_by_params_response['massage']}, status=status.HTTP_404_NOT_FOUND)
        if not filtered_startups.exists():
            return Response({"error": "Startups not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = StartupListSerializer(filtered_startups, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def filter_queryset_by_params(self, queryset, query_params):
        # Example URL: /api/startups/?industry=test
        # Example URL: /api/startups/?name=test
        industry = query_params.get('industry')
        name = query_params.get('name')
        other_params = query_params.keys() - {'industry', 'name'}
        if other_params:
            return {"queryset": queryset.none(), "status": "error",
                    "massage": f"Only 'industry' and 'name' parameters are allowed"}
        if industry:
            queryset = queryset.filter(industries__name__icontains=industry)
            if not queryset.exists():
                return {"queryset": queryset.none(), "status": "error",
                        "massage": f"No startups found for the industry '{industry}'"}
        if name:
            queryset = queryset.filter(startup_name__icontains=name)
            if not queryset.exists():
                return {"queryset": queryset.none(), "status": "error",
                        "massage": f"No startups found with the name '{name}'"}
        return {"queryset": queryset, "status": "success", "massage": ""}

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
        industry_name = request.data.get('industries')
        industry = get_object_or_404(Industry, name=industry_name)
        if existing_startup:
            return Response({"error": "Startup already exists for this user"}, status=status.HTTP_400_BAD_REQUEST)
        startup_info = request.data
        startup_info['industries'] = industry.id
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
            industry_name = request.data.get('industries')
            if industry_name:
                industry = Industry.objects.get(name=industry_name)
            else:
                industry = None
            serializer = StartupSerializerUpdate(startup, data=request.data, partial=False)
            serializer.is_valid(raise_exception=True)
            if industry is not None:
                serializer.validated_data['industries'] = industry
            serializer.save()
            if not startup.is_active:
                raise ValidationError({"error": "Startup not active"})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Industry.DoesNotExist:
            raise NotFound("Industry '{}' not found".format(industry_name))
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        # Example URL: /api/startups/2/
        # Update info about startup
        try:
            startup = get_object_or_404(Startup, id=pk)
            industry_name = request.data.get('industries')
            if industry_name:
                industry = Industry.objects.get(name=industry_name)
            else:
                industry = None
            serializer = StartupSerializerUpdate(startup, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            if industry is not None:
                serializer.validated_data['industries'] = industry
            serializer.save()
            if not startup.is_active:
                raise ValidationError({"error": "Startup not active"})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Industry.DoesNotExist:
            raise NotFound("Industry '{}' not found".format(industry_name))
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
