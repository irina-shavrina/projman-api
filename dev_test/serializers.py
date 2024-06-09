from rest_framework import serializers
from .models import Image

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ('id', 'title', 'image', 'uploaded_at')


    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['image_url'] = self.context['request'].build_absolute_uri(instance.image.url)
        return representation