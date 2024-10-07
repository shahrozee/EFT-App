from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LoginViewSet, UserSignupViewSet

router = DefaultRouter()

router.register(r'signup', UserSignupViewSet, basename='user-signup')
router.register(r'login', LoginViewSet, basename='user-login')

urlpatterns = [
    path('', include(router.urls)),
]
