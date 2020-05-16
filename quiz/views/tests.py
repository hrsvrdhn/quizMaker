import requests
import datetime
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, Http404, HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.urls import reverse

from accounts.models import UserProfile
from analytics.signals import object_viewed_signal
from quiz.forms import AddQuizForm, AddTestForm
from quiz.models import Test, TestStat, Feedback, Comment, Question
from quiz.serializers import TestSerializerForHome, TestSerializer
from quiz.utils import random_key_generator, rest_login_required_or_404, feedback_mail
from quiz.constants import PageTitle
from quiz.views.common_view_utils import build_user_context, perform_test_complete_operations, can_take_quiz, \
    is_user_owner_of_test, \
    get_object_or_none, wrap_with_internal_service_exception, build_repsonse_with_message, get_object_or_404_status_response

from topic.models import Topic
from topic.serializers import TopicSerializer
from secrets import compare_digest


@login_required
def manage_test(request, pk=None):
    user_profile = get_object_or_404(UserProfile, user__user=request.user)
    if request.method == "POST":
        return
    question_form = AddQuizForm()
    test = get_object_or_404(Test, pk=pk, owner=user_profile)
    all_topics = Topic.objects.exclude(tests=test)
    return render(
        request,
        "manageTest.html",
        {
            "all_topics": all_topics,
            "qform": question_form,
            "test": test,
            "user_context": build_user_context(request.user, PageTitle.MY_TEST),
        },
    )


@api_view(["POST"])
@rest_login_required_or_404
@wrap_with_internal_service_exception
def add_test_form(request):
    user_profile = get_object_or_404_status_response(UserProfile, user__user=request.user)
    serializer = TestSerializer(data=request.data)
    if not serializer.is_valid():
        return build_repsonse_with_message("Invalid request", response_status=status.HTTP_400_BAD_REQUEST)
    serializer.save(owner=user_profile)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["DELETE"])
@rest_login_required_or_404
@wrap_with_internal_service_exception
def delete_test(request, pk):
    user_profile = get_object_or_404_status_response(UserProfile, user__user=request.user)
    test = get_object_or_404_status_response(Test, pk=pk, owner=user_profile, publish=False)
    test.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET"])
@rest_login_required_or_404
@wrap_with_internal_service_exception
def new_test(request):
    new_tests = Test.objects.filter(
        publish=True, is_active=True, private=False
    ).order_by("-created_on")
    user_profile = get_object_or_404_status_response(UserProfile, user__user=request.user)
    new_tests = new_tests.exclude(owner=user_profile)[:5]

    serializer = TestSerializerForHome(new_tests, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["PUT"])
@rest_login_required_or_404
@wrap_with_internal_service_exception
def toggle_test_active(request, pk):
    user_profile = get_object_or_404_status_response(UserProfile, user__user=request.user)
    test = get_object_or_404_status_response(Test, pk=pk, owner=user_profile, publish=True)
    test.is_active = not test.is_active
    test.save()
    return Response({"active": test.is_active}, status=status.HTTP_200_OK)


@api_view(["PUT"])
@rest_login_required_or_404
@wrap_with_internal_service_exception
def toggle_test_private(request, pk):
    user_profile = get_object_or_404_status_response(UserProfile, user__user=request.user)
    test = get_object_or_404_status_response(Test, pk=pk, owner=user_profile, publish=False)

    test.private = not test.private
    # check if it's set to private for the first time, then generate token
    if not test.private_key or len(test.private_key) == 0:
        test.private_key = random_key_generator()
    test.save()
    return Response({"private": test.private}, status=status.HTTP_200_OK)


@api_view(["PUT"])
@rest_login_required_or_404
@wrap_with_internal_service_exception
def toggle_test_publish(request, pk):
    user_profile = get_object_or_404_status_response(UserProfile, user__user=request.user)
    test = get_object_or_404_status_response(Test, pk=pk, owner=user_profile)
    if test.questions.count() == 0:
        return build_repsonse_with_message("Empty question list.", response_status=status.HTTP_400_BAD_REQUEST)
    test.publish = True
    test.is_active = True
    test.published_on = timezone.now()
    test.save()
    return Response({"published": test.publish}, status=status.HTTP_200_OK)


@api_view(["POST"])
@rest_login_required_or_404
@wrap_with_internal_service_exception
def test_feedback(request, pk):
    test = get_object_or_404_status_response(Test, publish=True, pk=pk)
    user_profile = get_object_or_404_status_response(UserProfile, user__user=request.user)
    get_object_or_404_status_response(
        TestStat, test=test, candidate=user_profile, has_completed=True
    )
    if Feedback.objects.filter(test=test, candidate=user_profile).exists():
        return build_repsonse_with_message("Feedback already submitted.", response_status=status.HTTP_400_BAD_REQUEST)

    rating_int = int(request.POST.get("rating"))
    message = request.POST.get("message", None)

    if 0 <= rating_int <= 5:
        return build_repsonse_with_message("Rating out of expected bound.", response_status=status.HTTP_400_BAD_REQUEST)

    feedback = Feedback.objects.create(
        test=test,
        candidate=user_profile,
        rating=rating_int,
        message=message,
    )
    feedback_mail(feedback)
    return Response(status=status.HTTP_201_CREATED)


@api_view(["GET"])
@rest_login_required_or_404
@wrap_with_internal_service_exception
def recommended_test(request):
    user_profile = get_object_or_404_status_response(UserProfile, user__user=request.user)
    recommended_tests = sorted(
        Test.objects.recommended(user_profile),
        key=lambda x: x.get_average_rating,
        reverse=True,
    )
    serializer = TestSerializerForHome(recommended_tests, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
@wrap_with_internal_service_exception
def most_popular_test(request):
    most_popular = Test.objects.filter(publish=True, is_active=True, private=False)

    if request.user.is_authenticated:
        user_profile = get_object_or_404_status_response(UserProfile, user__user=request.user)
        most_popular = most_popular.exclude(owner=user_profile)

    most_popular_sorted = sorted(most_popular, key=lambda test: test.get_attempts(), reverse=True)[:5]
    serializer = TestSerializerForHome(most_popular_sorted, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def test_detail(request, pk):
    test = get_object_or_404(Test, publish=True, pk=pk)

    token = request.GET.get("token", None)
    if test.private and not compare_digest(test.private_key, token):
        raise Http404

    teststats = TestStat.objects.filter(test=test, has_completed=True).order_by(
        "-score"
    )

    comments = Comment.objects.filter(test=test).order_by("created_on")

    show_leaderboard = not test.private
    context = {
        "test": test,
        "teststats": teststats,
        "meta_application_name": test.name + "|",
        "show_leaderboard": show_leaderboard,
        "comments": comments,
        "current_datetime": datetime.datetime.now()
    }
    if request.user.is_authenticated:
        user_profile = get_object_or_404(UserProfile, user__user=request.user)
        try:
            user_teststat = TestStat.objects.get(test=test, candidate=user_profile)
        except:
            user_teststat = None
        if test.owner == user_profile:
            context["show_leaderboard"] = True
        context["user_teststat"] = user_teststat
        context["user_context"] = build_user_context(request.user, test.name)

    object_viewed_signal.send(test.__class__, instance=test, request=request)
    return render(request, "testDetail.html", context)


@require_http_methods(["GET"])
def all_tests(request):
    topic = request.GET.get("topic", None)
    topics = Topic.objects.all()
    tests = Test.objects.filter(publish=True, is_active=True, private=False)
    context = {"topic": topic, "topics": topics, "tests": tests}
    if request.user.is_authenticated:
        user_profile = get_object_or_404(UserProfile, user__user=request.user)
        try:
            user_profile_pic_url = requests.get(user_profile.user.get_avatar_url()).url
        except:
            pass
        user_context = {
            "name": user_profile.user.extra_data["name"],
            "profile_pic": user_profile_pic_url,
            "pageTitle": user_profile.user.extra_data["name"],
        }
        context["user_context"] = user_context
    return render(request, "alltest.html", context)


@login_required
@require_http_methods(["POST"])
def end_test(request, pk):
    test = get_object_or_404(Test, pk=pk)
    user_profile = get_object_or_404(UserProfile, user__user=request.user)
    test_stat = get_object_or_404(TestStat, test=test, candidate=user_profile)
    perform_test_complete_operations(test_stat)
    return HttpResponsePermanentRedirect(test.get_test_taking_url())



@login_required
def my_test(request):
    user_profile = get_object_or_404(UserProfile, user__user=request.user)
    tests = Test.objects.filter(owner=user_profile)
    return render(request, "mytest.html", {"tests": tests, "testForm": AddTestForm(),
                                           "user_context": build_user_context(request.user, PageTitle.MY_TEST)})


@login_required
def take_quiz(request, pk):
    test = get_object_or_404(Test, pk=pk)
    user_profile = get_object_or_404(UserProfile, user__user=request.user)
    token = request.GET.get("token", None)

    # owner of the test cannot take quiz, redirect owner to manage test page
    if is_user_owner_of_test(user_profile, test):
        return HttpResponseRedirect(reverse("quiz:manageTest", args=[pk]))

    # check if user can take this quiz or raise Http404
    if not can_take_quiz(test, user_profile, token):
        raise Http404
    teststat, created = TestStat.objects.get_or_create(
        test=test, candidate=user_profile
    )

    # find if user has submitted feedback already
    feedback = get_object_or_none(Feedback, test=test, candidate=user_profile)

    context = {
        "testno": test.id,
        "score": teststat.get_round_off_score(),
        "has_completed": teststat.has_completed,
        "no_of_questions": range(Question.objects.filter(test=test).count()),
        "feedback": getattr(feedback, "rating", None),
        "user_context": build_user_context(request.user, test.name),
    }
    return render(request, "quizDashboard.html", context)


@rest_login_required_or_404
@api_view(["POST"])
def add_test_topic(request, pk):
    user_profile = get_object_or_404(UserProfile, user__user=request.user)
    test = get_object_or_404(Test, pk=pk, owner=user_profile)
    serializer = TopicSerializer(data=request.data)
    if serializer.is_valid() and serializer.validated_data["name"].isalnum() and test.topics.count() < 10:
        topic, created = Topic.objects.get_or_create(
            name=serializer.validated_data["name"]
        )
        if created:
            test.topics.add(topic)
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@rest_login_required_or_404
@api_view(["DELETE"])
def delete_test_topic(request, pk):
    user_profile = get_object_or_404(UserProfile, user__user=request.user)
    serializer = TopicSerializer(data=request.data)
    if serializer.is_valid():
        topic = get_object_or_404(Topic, name=serializer.validated_data["name"])
        test = get_object_or_404(Test, pk=pk, owner=user_profile)
        test.topics.remove(topic)
        return Response(status=status.HTTP_200_OK)
    return Response(status=status.HTTP_400_BAD_REQUEST)
