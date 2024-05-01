from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from .models import Startup, Industry
from .serializers import StartupListSerializer


def list(self, request):
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
    industry = query_params.get('industry')
    name = query_params.get('name')
    other_params = query_params.keys() - {'industry', 'name'}
    if other_params:
        return {"queryset": queryset.none(), "status": "error", "massage": f"Only 'industry' and 'name' parameters are allowed"}
    if industry:
        queryset = queryset.filter(industries__name__icontains=industry)
        if not queryset.exists():
            return {"queryset": queryset.none(), "status": "error", "massage": f"No startups found for the industry '{industry}'"}
    if name:
        queryset = queryset.filter(startup_name__icontains=name)
        if not queryset.exists():
            return {"queryset": queryset.none(), "status": "error", "massage": f"No startups found with the name '{name}'"}
    return {"queryset": queryset, "status": "success", "massage": ""}
