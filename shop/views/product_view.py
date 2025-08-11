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

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = ExpressLikePagination

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [IsAdmin()]

    def get_queryset(self):
        qs = Product.objects.all()
        name = self.request.query_params.get("name", "").strip()
        min_price = self.request.query_params.get("minPrice")
        max_price = self.request.query_params.get("maxPrice")

        if name:
            qs = qs.filter(name__icontains=name)
        if min_price:
            qs = qs.filter(price__gte=min_price)
        if max_price:
            qs = qs.filter(price__lte=max_price)
        return qs

    @action(detail=False, methods=["post"], permission_classes=[IsAdmin], url_path="bulk")
    def bulk(self, request):
        """
        Accepts an array of products. Validates each, skips duplicates by name,
        and returns counts mirroring your Express route.
        """
        items = request.data
        if not isinstance(items, list) or not items:
            return Response({"error": "Request body must be a non-empty array of products"}, status=400)

        invalid = []
        valid = []

        # Step 1: validate each product
        for product in items:
            ser = ProductSerializer(data=product)
            if ser.is_valid():
                valid.append(ser.validated_data)
            else:
                invalid.append({"product": product, "error": ser.errors})

        # Step 2: filter out duplicates by name (case-sensitive like Node)
        names = [v["name"] for v in valid]
        existing_names = set(Product.objects.filter(name__in=names).values_list("name", flat=True))
        unique = [v for v in valid if v["name"] not in existing_names]
        skipped = [v for v in valid if v["name"] in existing_names]

        # Step 3: insert unique products
        created = []
        try:
            with transaction.atomic():
                objs = [Product(**v) for v in unique]
                created = Product.objects.bulk_create(objs, ignore_conflicts=False)
        except IntegrityError:
            pass

        return Response({
            "insertedCount": len(created),
            "skippedDuplicateCount": len(skipped),
            "invalidCount": len(invalid),
            "insertedProducts": ProductSerializer(created, many=True).data,
            "skippedDuplicates": skipped,
            "invalidProducts": invalid,
        }, status=status.HTTP_201_CREATED)
