from rest_framework import serializers
from .models import Image

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ('id', 'title', 'image', 'uploaded_at')

    # Если необходимо, можно добавить кастомное поле, которое возвращает полный путь
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Добавляем абсолютный URL, если требуется
        representation['image_url'] = self.context['request'].build_absolute_uri(instance.image.url)
        return representation