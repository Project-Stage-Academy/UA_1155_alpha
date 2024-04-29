from django.db import transaction
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response

from .models import Investor
from .serializers import InvestorSerializer


class IsInvestorPermission(permissions.BasePermission):
    """
    Custom permission to only allow investors to interact with the view.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated


class InvestorViewSet(viewsets.ViewSet):
    def get_permissions(self):
        if self.action == 'list' or self.action == 'retrieve':
            return []
        else:
            return [IsInvestorPermission()]

    def list(self, request):
        investors = Investor.objects.all()
        serializer = InvestorSerializer(investors, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        try:
            investor = Investor.objects.get(id=pk)
        except Investor.DoesNotExist:
            return Response({'error': 'Investor not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = InvestorSerializer(investor)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        serializer = InvestorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        try:
            investor = Investor.objects.get(id=pk)
        except Investor.DoesNotExist:
            return Response({'error': 'Investor not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = InvestorSerializer(instance=investor, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        try:
            investor = Investor.objects.get(id=pk)
        except Investor.DoesNotExist:
            return Response({'error': 'Investor not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = InvestorSerializer(instance=investor, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        try:
            with transaction.atomic():
                investor = Investor.objects.select_related('user').get(id=pk)
                investor.user.is_investor = 0
                investor.user.save()
                investor.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Investor.DoesNotExist:
            return Response({'error': 'Investor not found'}, status=status.HTTP_404_NOT_FOUND)

