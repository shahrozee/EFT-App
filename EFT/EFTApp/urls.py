from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserSignupViewSet, LoginViewSet, PasswordResetView, PasswordResetConfirmView, password_reset_form, logout, ContactUsAPIView, UserListAPIView, UserProfileUpdateAPIView, UserTherapyInfoAPIView, SubscriptionListView, SubscriptionCreateView, GoogleLogin, AppleLogin

router = DefaultRouter()

# Register only viewsets with the router
router.register(r'signup', UserSignupViewSet, basename='user-signup')
router.register(r'login', LoginViewSet, basename='user-login')

urlpatterns = [
    path('', include(router.urls)),
    path('reset-password/', PasswordResetView.as_view(), name='password_reset'),
    path('reset-password/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset-password/form/<str:uid>/', password_reset_form, name='password_reset_form'),
    path('logout/', logout, name='logout'),
    path('contact-us/', ContactUsAPIView.as_view(), name='contact_us'),
    path('users/', UserListAPIView.as_view(), name='user_list'),  # Use path for APIViews
    path('profile/update/', UserProfileUpdateAPIView.as_view(), name='profile-update'),
    path('user_therapy_info/', UserTherapyInfoAPIView.as_view(), name='user_therapy_info'),
    path('subscriptions/', SubscriptionListView.as_view(), name='subscription-list'),
    path('subscriptions/create/', SubscriptionCreateView.as_view(), name='subscription-create'),
    path('google_login/', GoogleLogin.as_view(), name='google_login'),
    path('apple_login/', AppleLogin.as_view(), name='apple-login'),
]
