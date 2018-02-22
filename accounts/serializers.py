from rest_framework import serializers
from .models import WebFeedback, UserProfile

class WebFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebFeedback
        fields = "__all__"

class TopScorerSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="user.extra_data.name", read_only=True)
    total_score = serializers.IntegerField(source="get_correct_response_count")
    username = serializers.CharField(source="user.user.username", read_only=True)
    class Meta:
        model = UserProfile
        fields = ('name', 'total_score', 'username')