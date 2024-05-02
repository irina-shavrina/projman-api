from django.urls import path
from . import views

urlpatterns = [
    path('', views.ImageListCreateView.as_view()),  # Маршрут для API
    path('<int:pk>/', views.ImageRetrieveView.as_view())
]