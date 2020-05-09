import csv
from io import StringIO
from random import shuffle

import bleach
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from accounts.models import UserProfile
from quiz.models import Test, Question, TestStat, QuestionStat
from quiz.serializers import (
    QuestionSerializer,
    QuestionListSerializer,
    QuestionStatSerializer,
)
from quiz.views import get_object_or_404_status_response, is_user_owner_of_test, has_attempted_test


@login_required
@api_view(["GET", "PUT", "DELETE"])
def update_question_form(request, tpk=None, qpk=None):
    user_profile = get_object_or_404(UserProfile, user__user=request.user)
    test = get_object_or_404_status_response(Test, pk=tpk, owner=user_profile)
    question = get_object_or_404_status_response(Question, pk=qpk, test=test)

    if request.method == "GET":
        return Response(QuestionSerializer(question).data)

    elif request.method == "PUT":
        if test.publish:
            raise Http404
        serializer = QuestionSerializer(question, data=request.data)
        if not serializer.is_valid():
            return Response({"message" : "Please enter valid values"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            serializer.save()
        except ValidationError as e:
            return Response({"message" : e.message}, status=status.HTTP_400_BAD_REQUEST)
        questions = Test.objects.get(pk=tpk, owner=user_profile).questions.all()
        serializer = QuestionListSerializer(questions, many=True)
        return Response(serializer.data)

    elif request.method == "DELETE":
        if test.publish:
            raise Http404
        question.delete()
        questions = Test.objects.get(pk=tpk, owner=user_profile).questions.all()
        serializer = QuestionListSerializer(questions, many=True)
        return Response(serializer.data)


@login_required
@api_view(["POST"])
def add_question_form(request, pk):
    user_profile = get_object_or_404(UserProfile, user__user=request.user)
    test = get_object_or_404_status_response(Test, pk=pk, owner=user_profile, publish=False)
    serializer = QuestionSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    serializer.save(test=test)
    questions = Question.objects.filter(
        test=Test.objects.get(pk=pk, owner=user_profile)
    )
    return Response(QuestionListSerializer(questions, many=True).data)


@login_required
@api_view(["GET"])
def get_question_list(request, pk):
    user_profile = get_object_or_404(UserProfile, user__user=request.user)
    test = get_object_or_404_status_response(Test, pk=pk)
    questions = Question.objects.filter(test=test)

    if not (has_attempted_test(user_profile, test) or is_user_owner_of_test(user_profile, test)):
        return Response(status=status.HTTP_404_NOT_FOUND)
    questions_serializer = QuestionListSerializer(questions, many=True)
    for question_serializer in questions_serializer.data:
        option_list = [
            question_serializer["option1"],
            question_serializer["option2"],
            question_serializer["option3"],
            question_serializer["option4"],
        ]
        shuffle(option_list)
        for i in range(4):
            question_serializer["option" + str(i + 1)] = bleach.clean(option_list[i])
    return Response(questions_serializer.data)


@login_required
@api_view(["GET", "POST"])
def question_stat_form(request, qpk):
    question = get_object_or_404(Question, pk=qpk)
    user_profile = get_object_or_404(UserProfile, user__user=request.user)
    test_stats = get_object_or_404(TestStat, test=question.test, candidate=user_profile)
    questionstat, created = QuestionStat.objects.get_or_create(
        question=question, candidate=user_profile
    )
    if request.method == "GET":
        if test_stats.has_completed:
            questionstat.correct_answer = question.correct_answer
        serializer = QuestionStatSerializer(questionstat)
        return Response(serializer.data)
    elif request.method == "POST" and not test_stats.has_completed:
        user_response = request.POST.get("option", None)
        if user_response:
            questionstat.response = user_response
        questionstat.save()
        return Response(status=status.HTTP_201_CREATED)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def csv_bulk_upload(request, pk):
    user_profile = get_object_or_404(UserProfile, user__user=request.user)
    try:
        test = Test.objects.get(pk=pk, owner=user_profile)
    except Test.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if test.publish:
        raise Http404
    try:
        csvf = StringIO(request.FILES["csv_file"].read().decode())
        csv_reader = csv.reader(csvf, delimiter=",")
        questions = []
        valid = True
        for row in csv_reader:
            if len(row) != 5:
                valid = False
                break
            questions.append(row)

        if not valid:
            return Response(
                {"message": "File not valid"}, status=status.HTTP_400_BAD_REQUEST
            )

        for qq in questions:
            Question.objects.create(
                question=qq[0],
                wrong_answer_1=qq[1],
                wrong_answer_2=qq[2],
                wrong_answer_3=qq[3],
                correct_answer=qq[4],
                test=test,
            )
        return Response({"data": "Success"})
    except ValidationError as ex:
        return Response(
            {"message": ex.message}, status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {"message": e.message}, status=status.HTTP_400_BAD_REQUEST
        )
