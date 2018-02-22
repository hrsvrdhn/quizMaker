import requests, bleach

from django.shortcuts import render, HttpResponse, get_object_or_404, HttpResponseRedirect, HttpResponsePermanentRedirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.core import serializers
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_http_methods
from django.conf import settings

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import UserProfile, WebFeedback
from .serializers import WebFeedbackSerializer, TopScorerSerializer
from topic.models import Topic
from topic.serializers import TopicSerializer
from quiz.models import TestStat
# Create your views here.

def NotFound(request, *args, **kwargs):
    if request.is_ajax():
        return Response(status=status.HTTP_404_NOT_FOUND)
    return render(request, '404.html',status=404)

def ServerError(request, *args, **kwargs):
    if request.is_ajax():
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return render(request, '500.html', status=500)

def BadRequest(request, *args, **kwargs):
    if request.is_ajax():
        return Response(status=status.HTTP_400_BAD_REQUEST)
    return render(request, '400.html', status=400)        

@api_view(['POST'])
def WebsiteFeedback(request):
    feedback = WebFeedbackSerializer(data=request.data)
    if feedback.is_valid():
        recaptcha_response = request.data.get("g-recaptcha-response", "")
        try:
            values = {
                'secret': getattr(settings, "GOOGLE_RECAPTCHA_SECRET_KEY", ""),
                'response': recaptcha_response
            }
            r = requests.post("https://www.google.com/recaptcha/api/siteverify", data=values)
        except:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if r.json().get("success"):
            feedback.save()
            return Response(status=status.HTTP_200_OK)
        else:
            print(r.json().get("error-codes"))
    return Response(status=status.HTTP_400_BAD_REQUEST) 

@login_required
def myProfile(request):
    return HttpResponsePermanentRedirect(reverse('user:profile', kwargs={'username': request.user.username}))

def Profile(request, username=None):
    profile = get_object_or_404(UserProfile, user__user__username=username)
    owner = False
    r = tests_taken = None
    try:
        user_profile = UserProfile.objects.get(user__user=request.user)
        following = UserProfile.objects.is_following(user_profile, profile)
        if user_profile == profile:
            owner = True
            tests_taken = TestStat.objects.filter(candidate=user_profile)
        r = requests.get(profile.user.get_avatar_url()).url
    except:
        following = False
    user_context =  {
        'name': profile.user.extra_data['name'],
        'profile_pic': r,
        'pageTitle': profile.user.extra_data['name'], 
    }
    context = {
        'name': profile.user.extra_data.get('name', None),
        'email': profile.user.extra_data.get('email', None),
        'owner': owner,
        'profile_pic': r,
        'get_follow_url': profile.get_follow_url,
        'following': following,
        'is_owner': request.user.username == username,
        'topics': profile.topics.all(),
        'all_topics': Topic.objects.exclude(liked_by=profile),
        'tests_taken': tests_taken,
        'total_tests_taken': profile.get_total_tests_taken,
        'questions_attempted_count': profile.get_attempts_count(),
        'correct_reponse_count': profile.get_correct_response_count(),
        'wrong_response_count': profile.get_wrong_response_count(),
        'accuracy': profile.get_accuracy(),
        'user_context': user_context,
    }
    return render(request, 'profile.html', context)

@api_view(['POST'])
def UserFollowView(request, username):
    toggle_user = get_object_or_404(UserProfile, user__user__username__iexact=username)
    if request.user.is_authenticated:
        is_following = UserProfile.objects.toggle_follow(request.user, toggle_user)
        return Response({'is_following': is_following} ,status=status.HTTP_200_OK)
    return Response(status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def TopScorers(request):
    users = sorted(UserProfile.objects.filter(teststats__isnull=False).distinct(), key=lambda x:x.get_correct_response_count(), reverse=True)[:3]
    serializer = TopScorerSerializer(users, many=True)
    return Response(serializer.data)
