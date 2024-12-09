from django.core.validators import MinLengthValidator
from rest_framework_simplejwt.tokens import RefreshToken

from rest_framework import serializers
from .models import (
    Profile, Contact, Project,
    ProjectFile, Status, Task, TaskFile,
    ProjectMessage, TaskMessage,ProjectMember
)
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )

        return user


class UserProfileSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(write_only=True, min_length=8)

    first_name = serializers.CharField(max_length=255)
    last_name = serializers.CharField(max_length=255)
    avatar = serializers.ImageField(required=False, allow_null=True)


    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists.")
        return value

    def create(self, validated_data):
        username = validated_data.pop("username")
        password = validated_data.pop("password")
        user = User.objects.create_user(username=username, password=password)

        profile_data = {
            "first_name": validated_data.pop("first_name"),
            "last_name": validated_data.pop("last_name"),
            "avatar": validated_data.pop("avatar", None),
        }
        profile = Profile.objects.create(user=user, **profile_data)

        return profile


class TokenSerializer(serializers.Serializer):
    token = serializers.CharField()

    def get_tokens_for_user(self, user):
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Profile
        fields = ['user', 'username', 'avatar', 'first_name', 'last_name']

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'soft_deadline', 'deadline', 'created_at', 'updated_at']

class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = ['id', 'name', 'project']
class TaskSerializer(serializers.ModelSerializer):
    status = serializers.PrimaryKeyRelatedField(queryset=Status.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Task
        fields = ['id', 'name', 'description', 'soft_deadline', 'deadline', 'created_at', 'updated_at', 'creator', 'performer', 'status']

    def create(self, validated_data):
        # Установить статус как None при создании
        validated_data['status'] = None
        return super().create(validated_data)


class ContactSerializer(serializers.ModelSerializer):
    to_profile = ProfileSerializer()

    class Meta:
        model = Contact
        fields = ['to_profile']

class ProjectFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectFile
        fields = ['id', 'file', 'description', 'uploaded_at']

class TaskFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskFile
        fields = ['id', 'file', 'description', 'uploaded_at']

class ProjectMessageSerializer(serializers.ModelSerializer):
    author = ProfileSerializer()
    related_file = ProjectFileSerializer()

    class Meta:
        model = ProjectMessage
        fields = ['id', 'author', 'project', 'related_comment', 'related_file', 'content', 'time_create', 'time_update']

class TaskMessageSerializer(serializers.ModelSerializer):
    author = ProfileSerializer()
    related_file = TaskFileSerializer()

    class Meta:
        model = TaskMessage
        fields = ['id', 'author', 'task', 'related_comment', 'related_file', 'content', 'time_create', 'time_update']



