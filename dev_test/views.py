from rest_framework import generics
from rest_framework.permissions import AllowAny

from .models import Image
from .serializers import ImageSerializer

class ImageListCreateView(generics.ListCreateAPIView):
    permission_classes = [AllowAny]
    queryset = Image.objects.all()
    serializer_class = ImageSerializer

    def post(self, request, *args, **kwargs):
        print(request.data)
        return super().post(request, *args, **kwargs)


class ImageRetrieveView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    queryset = Image.objects.all()
    serializer_class = ImageSerializer

    def get(self, request, *args, **kwargs):
        print(request.data)
        return super().get(request, *args, **kwargs)


