from django.shortcuts import render, HttpResponse, get_object_or_404, HttpResponseRedirect, HttpResponsePermanentRedirect
from django.http import Http404
from django.db.models import Count

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from accounts.models import UserProfile
from .models import Topic
from .serializers import TopicSerializer
# Create your views here.

@api_view(['POST'])
def AddTopic(request):
    if request.user.is_authenticated:
        serializer = TopicSerializer(data=request.data)
        if serializer.is_valid():
            if serializer.validated_data['name'].isalnum():
                topic, created = Topic.objects.get_or_create(name=serializer.validated_data['name'])
                profile = UserProfile.objects.get(user__user=request.user)
                profile.topics.add(topic)
                return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def RemoveTopic(request):
    if request.user.is_authenticated:
        serializer = TopicSerializer(data=request.data)
        if serializer.is_valid():
            topic = get_object_or_404(Topic, name=serializer.validated_data['name'])
            print(topic.liked_by.all())
            profile = UserProfile.objects.get(user__user=request.user)
            profile.topics.remove(topic)
            print(topic.liked_by.all())
            return Response(serializer.data, status=status.HTTP_200_OK)        
    return Response(status=status.HTTP_400_BAD_REQUEST)

from random import randint
@api_view(['GET'])
def countTopic(request):
    qs = Topic.objects.annotate(Count("tests")).exclude(tests__count=0)
    topic_name = [q.name for q in qs]
    topic_count = [q.tests__count for q in qs]
    colors = ["rgb({},{},{})".format(randint(1,255),randint(1,255),randint(1,255)) for _ in range(qs.count())]
    return Response({
        "name": topic_name,
        "count": topic_count,
        "colors": colors,
    })