from django.urls import path

from .views import RegisterView, LoginView, ProtectedResourceView, GetUserProfiles

urlpatterns = [
    path('profile/', GetUserProfiles.as_view(), name='profile'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('', ProtectedResourceView.as_view(), name='resource'),
]