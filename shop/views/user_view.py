from django.shortcuts import render

from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Product
from ..serializers import (
    ProductSerializer,
    AdminCreateSerializer,
    UserSafeSerializer,
)
from ..pagination import ExpressLikePagination
from ..permissions import IsAdmin

class AdminCreateView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request):
        ser = AdminCreateSerializer(data=request.data)
        if ser.is_valid():
            user = ser.save()
            return Response(UserSafeSerializer(user).data, status=201)
        return Response(ser.errors, status=400)

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all().order_by("id")
    serializer_class = UserSafeSerializer

    def get_permissions(self):
        return [IsAdmin()]  # only admins can list or retrieve users

class VerifyView(APIView):
    def get(self, request):
        if not request.user or not request.user.is_authenticated:
            return Response({"detail": "Not authenticated"}, status=401)
        return Response({
            "id": request.user.id,
            "username": request.user.username,
            "is_staff": request.user.is_staff,
        })