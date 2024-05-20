from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from projects.models import Project
from users.models import CustomUser
from .models import Startup, Industry
from .serializers import StartupListSerializer, StartupSerializer, StartupSerializerUpdate
from drf_yasg import openapi

class IsStartupPermission(permissions.BasePermission):
    """
    Custom permission to only allow startups to interact with the view.
    """

    def has_permission(self, request, view):
        return request.user.is_startup == 1 and request.user.is_authenticated


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

    def get_permissions(self):
        permission_list = ["list", "retrieve"]
        if self.action in permission_list:
            return []
        elif self.action == "create":
            return [IsAuthenticated()]
        return [IsStartupPermission()]

    @swagger_auto_schema(
        operation_summary="Retrieve a list of all startups",
        operation_description="Retrieve a list of all startups with optional filtering.",
        tags=["Startups"],
        responses={
            200: StartupListSerializer,
            400: "Bad Request"
        },
    )
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

    @swagger_auto_schema(
        operation_summary="Retrieve information about one startup by its ID",
        operation_description="Retrieve information about one startup by its ID.",
        tags=["Startups"],
        responses={
            200: StartupListSerializer,
            400: "Bad Request"
        },
    )
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

    @swagger_auto_schema(
        operation_summary="Create a new startup",
        operation_description="Create a new startup with the provided information.",
        tags=["Startups"],
        responses={
            201: StartupSerializer,
            400: "Bad Request"
        },
        request_body=StartupSerializer
    )
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

    @swagger_auto_schema(
        operation_summary="Fully update an existing startup by its ID",
        operation_description="Fully update an existing startup by its ID.",
        tags=["Startups"],
        responses={
            200: StartupSerializer,
            400: "Bad Request"
        },
        request_body=StartupSerializer
    )
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

    @swagger_auto_schema(
        operation_summary="Partially update an existing startup by its ID",
        operation_description="Partially update an existing startup by its ID.",
        tags=["Startups"],
        responses={
            200: StartupSerializer,
            400: "Bad Request"
        },
        request_body=StartupSerializer
    )
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

    @swagger_auto_schema(
        operation_summary="Delete a startup by its ID",
        operation_description="Delete a startup by its ID.",
        tags=["Startups"],
        responses={
            204: "No Content",
            400: "Bad Request",
            409: "Conflict"
        },
    )
    def destroy(self, request, pk=None):
        # Implementation of DELETE METHOD for one startup - ExampLE URL: /api/startups/4/
        # Do not forget about SLASH at the end of URL
        # Deleting logic
        startup = get_object_or_404(Startup, id=pk)
        projects_exist = Project.objects.filter(startup=startup.id, is_active=True).exists()

        if projects_exist:
            return Response({"detail": "Please delete all your projects first."},
                            status=status.HTTP_409_CONFLICT)

        startup.is_active = 0
        user_instance = startup.owner
        user_instance.is_startup = 0
        startup.save()
        user_instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        operation_summary="Retrieve information about the authenticated user's startup",
        operation_description="Retrieve information about the authenticated user's startup.",
        tags=["Startups"],
        responses={
            200: StartupSerializer,
            404: "Not Found"
        },
    )
    @action(detail=False, methods=["get"], url_path="profile")
    def get_my_profile(self, request):
        jwt_token = request.auth
        user_id = jwt_token.payload.get("id")
        user_instance = CustomUser.objects.get(id=user_id)

        startup = get_object_or_404(Startup, owner=user_instance, is_active=True)
        serializer = StartupSerializer(startup)

        return Response(serializer.data, status=status.HTTP_200_OK)
