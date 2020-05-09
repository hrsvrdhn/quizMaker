from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from accounts.models import UserProfile
from quiz.models import TestStat, Test
from quiz.utils import rest_login_required_or_404


@api_view(["GET"])
def score_distribution(requests, pk):
    test = get_object_or_404(Test, pk=pk)
    teststats = TestStat.objects.filter(test=test, has_completed=True)
    percentage = 0.2
    data = [teststats.filter(
        score__gte=(percentage - 0.2) * test.get_question_count(),
        score__lte=percentage * test.get_question_count(),
    ).count()]
    percentage += 0.2
    while percentage <= 1:
        data.append(
            teststats.filter(
                score__gt=(percentage - 0.2) * test.get_question_count(),
                score__lte=percentage * test.get_question_count(),
            ).count()
        )
        percentage += 0.2
    return Response({"data": data})


@rest_login_required_or_404
@api_view(["GET"])
def score_chart(request, pk):
    user_profile = get_object_or_404(UserProfile, user__user=request.user)
    test = get_object_or_404(Test, pk=pk)
    teststat = get_object_or_404(TestStat, candidate=user_profile, test=test)
    if teststat.has_completed:
        correct_count = teststat.get_correct_response_count()
        wrong_count = teststat.get_wrong_response_count()
        total = teststat.get_total_attempts()
        colors = ["rgb(0,255,0)", "rgb(255,0,0)", "rgb(105,105,105)"]
        return Response(
            {
                "correct_count": correct_count,
                "wrong_count": wrong_count,
                "total": total,
                "colors": colors,
            }
        )
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)