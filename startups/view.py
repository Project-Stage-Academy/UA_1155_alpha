from rest_framework import status
from rest_framework.response import Response

from .models import Startup
from .serializers import StartupListSerializer


def list(self, request):
    startups = Startup.objects.filter(is_active=True)
    try:
        startups = self.filter_queryset_by_params(startups, request.query_params)
        if not startups.exists():
            return Response({"error": "Startups not found"}, status=status.HTTP_404_NOT_FOUND)
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Startup.DoesNotExist as e:
        return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

    serializer = StartupListSerializer(startups, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


def filter_queryset_by_params(self, queryset, query_params):
    industry = query_params.get('industry')
    name = query_params.get('name')
    other_params = query_params.keys() - {'industry', 'name'}

    if other_params:
        raise ValueError("Only 'industry' and 'name' parameters are allowed")

    if industry:
        queryset = queryset.filter(industries__icontains=industry)
        if not queryset.exists():
            raise Startup.DoesNotExist(f"No startups found for the industry '{industry}'")

    if name:
        queryset = queryset.filter(startup_name__icontains=name)
        if not queryset.exists():
            raise Startup.DoesNotExist(f"No startups found with the name '{name}'")

    return queryset
