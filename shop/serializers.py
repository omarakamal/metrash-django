from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "price", "description", "image_url", "created_at", "updated_at"]

    def validate_price(self, value):
        if value is None or value < 0:
            raise serializers.ValidationError("Price must be >= 0")
        return value

class AdminCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ["id", "username", "password", "is_staff", "date_joined"]
        read_only_fields = ["id", "is_staff", "date_joined"]

    def create(self, validated_data):
        username = validated_data["username"]
        password = validated_data["password"]
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError({"username": "username already taken"})
        user = User(username=username, is_staff=True, is_superuser=False)
        user.set_password(password)
        user.save()
        return user

class UserSafeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "is_staff", "date_joined"]