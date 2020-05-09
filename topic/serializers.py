from rest_framework import serializers
from .models import Topic


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ("name",)

    def validate_name(self, value):
        if not value.isalnum():
            raise serializers.ValidationError("topic name should be alphanumeric")
        return value
