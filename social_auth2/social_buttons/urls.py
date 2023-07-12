from django.urls import path
from .views import GoogleLoginAPIView, GoogleCallbackAPIView, facebookLoginAPIView, facebookCallbackAPIView

urlpatterns = [
    path('google/login/', GoogleLoginAPIView.as_view(), name='google-login'),
    path('google/callback/', GoogleCallbackAPIView.as_view(), name='google-callback'),
    path("facebook/login", facebookLoginAPIView.as_view(), name='facebook_login'),
    path("facebook/callback", facebookCallbackAPIView.as_view(), name="callback"),
]
