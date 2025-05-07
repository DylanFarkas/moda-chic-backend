from django.urls import path, include
from products import views
from .views import RegisterView, LoginView, UserListView, WishlistView
from .views import PasswordResetRequestView, PasswordResetConfirmView
from rest_framework import routers


router = routers.DefaultRouter()
router.register(r'wishlist', WishlistView, 'wishlist')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('users/', UserListView.as_view(), name='users'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('', include(router.urls)),
]
