from django.shortcuts import get_object_or_404
from django.db.models import Count
from random import randint

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from accounts.models import UserProfile
from .models import Topic
from .serializers import TopicSerializer
from quiz.utils import rest_login_required_or_404
# Create your views here.


@rest_login_required_or_404
@api_view(["POST"])
def AddTopic(request):
    serializer = TopicSerializer(data=request.data)
    profile = UserProfile.objects.get(user__user=request.user)
    if not serializer.is_valid():
        return Response(status=status.HTTP_400_BAD_REQUEST)
    if profile.topics.count() < 10:
        response_data = {"message": "More than 10 topics not allowed."}
    else:
        response_data = serializer.data
        topic, created = Topic.objects.get_or_create(
            name=serializer.validated_data["name"]
        )
        profile.topics.add(topic)
    return Response(response_data, status=status.HTTP_200_OK)


@rest_login_required_or_404
@api_view(["DELETE"])
def RemoveTopic(request):
    serializer = TopicSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(status=status.HTTP_400_BAD_REQUEST)
    topic = get_object_or_404(Topic, name=serializer.validated_data["name"])
    profile = UserProfile.objects.get(user__user=request.user)
    profile.topics.remove(topic)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def countTopic(request):
    qs = (
        Topic.objects.filter(tests__publish=True, tests__private=False)
        .annotate(Count("tests"))
        .exclude(tests__count=0)
        .order_by("-tests__count")[:10]
    )
    topic_name = [q.name for q in qs]
    topic_count = [q.tests__count for q in qs]
    colors = [
        "rgb({},{},{})".format(randint(1, 255), randint(1, 255), randint(1, 255))
        for _ in range(qs.count())
    ]
    return Response({"name": topic_name, "count": topic_count, "colors": colors})