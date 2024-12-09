from django.contrib.auth.models import User
from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
status_ = status
from rest_framework.views import APIView
from django.db.models import Q

from django.contrib.auth import authenticate
from rest_framework.response import Response
from .models import (
    Project, Status, Task,
    Contact, ProjectMessage,
    ProjectFile, TaskMessage,
    TaskFile, Profile,
    ProjectMember
)
from .serializers import (
    UserProfileSerializer, TokenSerializer,
    ProjectSerializer, StatusSerializer, TaskSerializer,
    ContactSerializer, ProjectFileSerializer, TaskFileSerializer,
    ProjectMessageSerializer, TaskMessageSerializer, ProfileSerializer
)


class RegisterView(generics.CreateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        print(request.data)
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            profile = serializer.save()

            username = request.data.get('username')
            password = request.data.get('password')

            user = authenticate(username=username, password=password)

            token_serializer = TokenSerializer()
            tokens = token_serializer.get_tokens_for_user(user)
            return Response(tokens|{

                    "username": profile.user.username,
                    "first_name": profile.first_name,
                    "last_name": profile.last_name,
                    "avatar": request.build_absolute_uri(profile.avatar.url) if profile.avatar else None,

            }, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = TokenSerializer

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)

        if user is not None:
            token_serializer = self.serializer_class()
            tokens = token_serializer.get_tokens_for_user(user)

            profile = Profile.objects.get(user=user)
            profile_data = {
                'username': user.username,
                'first_name': profile.first_name,
                'last_name': profile.last_name,
                'avatar': request.build_absolute_uri(profile.avatar.url) if profile.avatar else None if profile.avatar else None,
            }
            return Response({**tokens, **profile_data})
        else:
            return Response({"error": "Invalid credentials"}, status=400)


class GetUserProfiles(generics.ListAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [AllowAny]
    queryset = Profile.objects.all()

    def get(self, request, *args, **kwargs):
        result = super().get(request, *args, **kwargs)
        return result


class ProtectedResourceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "message": "This is a protected resource!",
            "user": request.user.username
        })


class ProjectListView(generics.ListCreateAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user.profile
        return Project.objects.filter(Q(owner=user) | Q(members=user)).distinct()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user.profile)


class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user.profile
        return Project.objects.filter(Q(owner=user) | Q(members=user)).distinct()

    def perform_update(self, serializer):
        project = self.get_object()
        if project.owner == self.request.user.profile:
            serializer.save()
        else:
            raise PermissionDenied("You do not have permission to edit this project.")

    def perform_destroy(self, instance):
        if instance.owner == self.request.user.profile:
            instance.delete()
        else:
            raise PermissionDenied("You do not have permission to delete this project.")

class StatusListView(generics.ListCreateAPIView):
    serializer_class = StatusSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        project_id = self.kwargs.get('project_id')
        return Status.objects.filter(project_id=project_id)


class StatusDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = StatusSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        project_id = self.kwargs.get('project_id')
        return Status.objects.filter(project_id=project_id)

    def get_object(self):
        project_id = self.kwargs.get('project_id')
        status_id = self.kwargs.get('pk')
        return get_object_or_404(Status, project_id=project_id, pk=status_id)

    def put(self, request, *args, **kwargs):
        project_id = self.kwargs.get('project_id')
        request.data['project'] = project_id  # Add project_id to request data
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        project_id = self.kwargs.get('project_id')
        return self.destroy(request, *args, **kwargs)

class TaskListView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        project_id = self.kwargs['project_id']
        return Task.objects.filter(project_id=project_id).order_by('status')

    def perform_create(self, serializer):

        creator = self.kwargs.get('creator')
        performer = self.kwargs.get('performer')
        status = 0
        serializer.save(creator=creator,performer=performer,status=status)

    def post(self, request, *args, **kwargs):
        try:
            request.data['status'] = request.data['status']
        except:
            request.data['status'] = None
        request.data['creator'] = request.user.profile
        if request.data['performer'] is not None:
            request.data['performer'] = get_object_or_404(User, username=request.data['performer'])
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        project_id = self.kwargs['project_id']
        return Task.objects.filter(project_id=project_id)
class ContactListView(generics.ListAPIView):
    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Contact.objects.filter(from_profile=self.request.user.profile)

class ContactCreateDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, username, format=None):
        to_profile = Profile.objects.get(user__username=username)
        Contact.objects.create(from_profile=request.user.profile, to_profile=to_profile)
        return Response(status=status.HTTP_201_CREATED)

    def delete(self, request, username, format=None):
        to_profile = Profile.objects.get(user__username=username)
        Contact.objects.filter(from_profile=request.user.profile, to_profile=to_profile).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ProjectMemberListView(generics.ListCreateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        project_id = self.kwargs['project_id']
        return Profile.objects.filter(joined_projects__id=project_id)

    def post(self, request, project_id, username, format=None):
        project = Project.objects.get(id=project_id)
        if project.owner == request.user.profile:
            new_member = Profile.objects.get(user__username=username)
            ProjectMember.objects.create(member=new_member, project=project)
            return Response(status=status.HTTP_201_CREATED)
        else:
            raise PermissionDenied("You do not have permission to add members to this project.")

    def delete(self, request, project_id, username, format=None):
        project = Project.objects.get(id=project_id)
        if project.owner == request.user.profile:
            member = Profile.objects.get(user__username=username)
            ProjectMember.objects.filter(member=member, project=project).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise PermissionDenied("You do not have permission to remove members from this project.")

class ProjectMessageListView(generics.ListCreateAPIView):
    serializer_class = ProjectMessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        project_id = self.kwargs['project_id']
        user = self.request.user.profile
        project = Project.objects.get(id=project_id)
        if project.owner == user or user in project.members.all():
            return ProjectMessage.objects.filter(project_id=project_id)
        else:
            raise PermissionDenied("You do not have permission to view messages for this project.")

    def perform_create(self, serializer):
        project_id = self.kwargs['project_id']
        serializer.save(author=self.request.user.profile, project_id=project_id)

class ProjectMessageDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProjectMessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        project_id = self.kwargs['project_id']
        return ProjectMessage.objects.filter(project_id=project_id)

class ProjectFileListView(generics.ListCreateAPIView):
    serializer_class = ProjectFileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        project_id = self.kwargs['project_id']
        return ProjectFile.objects.filter(project_id=project_id)

    def perform_create(self, serializer):
        project_id = self.kwargs['project_id']
        serializer.save(project_id=project_id)

class ProjectFileDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = ProjectFileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        project_id = self.kwargs['project_id']
        return ProjectFile.objects.filter(project_id=project_id)

class TaskMessageListView(generics.ListCreateAPIView):
    serializer_class = TaskMessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        task_id = self.kwargs['task_id']
        project_id = self.kwargs['project_id']
        user = self.request.user.profile
        project = Project.objects.get(id=project_id)
        if project.owner == user or user in project.members.all():
            return TaskMessage.objects.filter(task_id=task_id)
        else:
            raise PermissionDenied("You do not have permission to view messages for this task.")

    def perform_create(self, serializer):
        task_id = self.kwargs['task_id']
        serializer.save(author=self.request.user.profile, task_id=task_id)

class TaskMessageDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskMessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        task_id = self.kwargs['task_id']
        return TaskMessage.objects.filter(task_id=task_id)

class TaskFileListView(generics.ListCreateAPIView):
    serializer_class = TaskFileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        task_id = self.kwargs['task_id']
        return TaskFile.objects.filter(task_id=task_id)

    def perform_create(self, serializer):
        task_id = self.kwargs['task_id']
        serializer.save(task_id=task_id)

class TaskFileDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = TaskFileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        task_id = self.kwargs['task_id']
        return TaskFile.objects.filter(task_id=task_id)
