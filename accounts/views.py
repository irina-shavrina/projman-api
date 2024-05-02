from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from .models import Profile
from .serializers import UserProfileSerializer, TokenSerializer
from django.contrib.auth import authenticate


class RegisterView(generics.CreateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            profile = serializer.save()
            return Response({
                "user": {
                    "username": profile.user.username,
                    "first_name": profile.first_name,
                    "last_name": profile.last_name,
                    "avatar": profile.avatar.url if profile.avatar else None,
                },
                "message": "User and profile created successfully."
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
            return Response(tokens)
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
