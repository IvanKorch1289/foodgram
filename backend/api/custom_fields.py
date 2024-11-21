import base64

from django.core.files.base import ContentFile
from rest_framework import serializers


class Base64ImageField(serializers.ImageField):
    """
    Кастомное поле для обработки изображений в формате Base64
    """

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            header, image_data = data.split(";base64,")
            extension = header.split("/")[-1]
            decoded_file = base64.b64decode(image_data)
            file = ContentFile(decoded_file, name=f"avatar.{extension}")
            return super().to_internal_value(file)
        raise serializers.ValidationError("Недопустимый формат изображения.")
