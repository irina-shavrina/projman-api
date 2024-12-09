from django.urls import path

from .views import (
    RegisterView, LoginView, ProtectedResourceView, GetUserProfiles,

    ProjectListView, ProjectDetailView, StatusListView, StatusDetailView,
    TaskListView, TaskDetailView, ContactListView, ContactCreateDeleteView,
    ProjectMemberListView, ProjectMessageListView, ProjectMessageDetailView,
    ProjectFileListView, ProjectFileDetailView, TaskMessageListView,
    TaskMessageDetailView, TaskFileListView, TaskFileDetailView
)


urlpatterns = [
    path('profile/', GetUserProfiles.as_view(), name='profile'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('', ProtectedResourceView.as_view(), name='resource'),

    path('projects/', ProjectListView.as_view(), name='project-list'),
    path('projects/<int:pk>/', ProjectDetailView.as_view(), name='project-detail'),
    path('projects/<int:project_id>/status/', StatusListView.as_view(), name='status-list'),
    path('projects/<int:project_id>/status/<int:pk>/', StatusDetailView.as_view(), name='status-detail'),
    path('projects/<int:project_id>/tasks/', TaskListView.as_view(), name='task-list'),
    path('projects/<int:project_id>/tasks/<int:pk>/', TaskDetailView.as_view(), name='task-detail'),
    path('contacts/', ContactListView.as_view(), name='contact-list'),
    path('contacts/<str:username>/', ContactCreateDeleteView.as_view(), name='contact-create-delete'),
    path('projects/<int:project_id>/members/', ProjectMemberListView.as_view(), name='project-member-list'),
    path('projects/<int:project_id>/messages/', ProjectMessageListView.as_view(), name='project-message-list'),
    path('projects/<int:project_id>/messages/<int:pk>/', ProjectMessageDetailView.as_view(), name='project-message-detail'),
    path('projects/<int:project_id>/files/', ProjectFileListView.as_view(), name='project-file-list'),
    path('projects/<int:project_id>/files/<int:pk>/', ProjectFileDetailView.as_view(), name='project-file-detail'),
    path('projects/<int:project_id>/tasks/<int:task_id>/messages/', TaskMessageListView.as_view(), name='task-message-list'),
    path('projects/<int:project_id>/tasks/<int:task_id>/messages/<int:pk>/', TaskMessageDetailView.as_view(), name='task-message-detail'),
    path('projects/<int:project_id>/tasks/<int:task_id>/files/', TaskFileListView.as_view(), name='task-file-list'),
    path('projects/<int:project_id>/tasks/<int:task_id>/files/<int:pk>/', TaskFileDetailView.as_view(), name='task-file-detail'),
]
