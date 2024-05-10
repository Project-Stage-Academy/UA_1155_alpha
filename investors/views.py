from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from users.models import CustomUser

from .models import Investor
from .serializers import InvestorSerializer


class IsInvestorPermission(permissions.BasePermission):
    """
    Custom permission to only allow investors to interact with the view.
    """

    def has_permission(self, request, view):
        return request.user.is_investor == 1 and request.user.is_authenticated


class InvestorViewSet(viewsets.ViewSet):
    def get_permissions(self):
        permission_list = ["list", "retrieve"]
        if self.action in permission_list:
            return []
        elif self.action == "create":
            return [IsAuthenticated()]
        return [IsInvestorPermission()]

    def list(self, request):
        investors = Investor.objects.filter(is_active=True)
        serializer = InvestorSerializer(investors, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        investor = get_object_or_404(Investor, id=pk, is_active=True)
        serializer = InvestorSerializer(investor)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        jwt_token = request.auth
        user_id = jwt_token.payload.get("id")

        existing_investor = Investor.objects.filter(user=user_id).first()
        if existing_investor:
            return Response({"error": "Investor already exists for this user"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = InvestorSerializer(data=request.data)
        if serializer.is_valid():
            user_instance = CustomUser.objects.get(id=user_id)
            user_instance.is_investor = 1
            user_instance.save()
            Investor.objects.create(user=user_instance, **serializer.validated_data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        investor = get_object_or_404(Investor, id=pk)
        serializer = InvestorSerializer(instance=investor, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        investor = get_object_or_404(Investor, id=pk)
        serializer = InvestorSerializer(
            instance=investor, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        investor = get_object_or_404(Investor, id=pk)
        investor.is_active = 0
        user_instance = investor.user
        user_instance.is_investor = 0

        with transaction.atomic():
            investor.save()
            user_instance.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"], url_path="profile")
    def get_my_profile(self, request):
        jwt_token = request.auth
        user_id = jwt_token.payload.get("id")
        user_instance = CustomUser.objects.get(id=user_id)

        investor = get_object_or_404(Investor, user=user_instance, is_active=True)
        serializer = InvestorSerializer(investor)

        return Response(serializer.data, status=status.HTTP_200_OK)

