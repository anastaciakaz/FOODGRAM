import base64
import uuid
import webcolors

from django.core.files.base import ContentFile

from rest_framework import serializers


class Base64ImageField(serializers.ImageField):
    """Класс для работы с base64 изображениями."""
    def to_internal_value(self, data):
        """Переопределение метода для декодирования строки в фото."""
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            id = uuid.uuid4()
            data = ContentFile(
                base64.b64decode(imgstr), name=id.urn[9:] + '.' + ext
            )
        return super().to_internal_value(data)


class Hex2NameColor(serializers.Field):
    """
    Класс для создания нового типа поля с цветом в формате hex
    при описании тегов.
    """
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')
        return data
