from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView

from .views.product_view import ProductViewSet
from .views.user_view import  AdminCreateView, UserViewSet, VerifyView

router = DefaultRouter()
router.register(r"products", ProductViewSet, basename="product")
router.register(r"users", UserViewSet, basename="user")

urlpatterns = [
    path("", include(router.urls)),
    path("auth/login", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/verify", VerifyView.as_view(), name="verify"),
    path("admins/create", AdminCreateView.as_view(), name="admin-create"),
]