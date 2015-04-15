from rest_framework.serializers import ModelSerializer
from .models import Rating


class RatingSerializer(ModelSerializer):
    class Meta:
        model = Rating
        fields = ('content_type_id', 'object_id', )
