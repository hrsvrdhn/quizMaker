from random import shuffle

import bleach
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.utils.datastructures import MultiValueDictKeyError
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
from quiz.utils import get_file_type, get_data_from_csv, get_data_from_excel, rest_login_required_or_404
from quiz.views.common_view_utils import get_object_or_404_status_response, is_user_owner_of_test, has_attempted_test, \
    build_repsonse_with_message, wrap_with_internal_service_exception


@api_view(["GET", "PUT", "DELETE"])
@rest_login_required_or_404
@wrap_with_internal_service_exception
def update_question_form(request, tpk=None, qpk=None):
    user_profile = get_object_or_404_status_response(UserProfile, user__user=request.user)
    test = get_object_or_404_status_response(Test, pk=tpk, owner=user_profile)
    question = get_object_or_404_status_response(Question, pk=qpk, test=test)

    if request.method == "GET":
        return Response(QuestionSerializer(question).data)

    elif request.method == "PUT":
        if test.publish:
            return build_repsonse_with_message("Cannot update question once test is published",
                                               response_status=status.HTTP_400_BAD_REQUEST)
        serializer = QuestionSerializer(question, data=request.data)
        if not serializer.is_valid():
            return build_repsonse_with_message("Enter valid values",
                                               response_status=status.HTTP_400_BAD_REQUEST)
        try:
            serializer.save()
        except ValidationError as e:
            return Response({"message": e.message}, status=status.HTTP_400_BAD_REQUEST)

        questions = Test.objects.get(pk=tpk, owner=user_profile).questions.all()
        serializer = QuestionListSerializer(questions, many=True)
        return Response(serializer.data)

    elif request.method == "DELETE":
        if test.publish:
            return build_repsonse_with_message("Cannot delete question once test is published",
                                               response_status=status.HTTP_400_BAD_REQUEST)
        question.delete()

        questions = Test.objects.get(pk=tpk, owner=user_profile).questions.all()
        serializer = QuestionListSerializer(questions, many=True)
        return Response(serializer.data)


@api_view(["POST"])
@rest_login_required_or_404
@wrap_with_internal_service_exception
def add_question_form(request, pk):
    user_profile = get_object_or_404_status_response(UserProfile, user__user=request.user)
    test = get_object_or_404_status_response(Test, pk=pk, owner=user_profile, publish=False)
    serializer = QuestionSerializer(data=request.data)

    if not serializer.is_valid():
        return build_repsonse_with_message("Enter valid values",
                                           response_status=status.HTTP_400_BAD_REQUEST)

    try:
        serializer.save(test=test)
    except ValidationError as e:
        return build_repsonse_with_message(e.message, response_status=status.HTTP_412_PRECONDITION_FAILED)
    questions = Question.objects.filter(
        test=Test.objects.get(pk=pk, owner=user_profile)
    )
    return Response(QuestionListSerializer(questions, many=True).data)


@api_view(["GET"])
@rest_login_required_or_404
@wrap_with_internal_service_exception
def get_question_list(request, pk):
    user_profile = get_object_or_404_status_response(UserProfile, user__user=request.user)
    test = get_object_or_404_status_response(Test, pk=pk)
    questions = Question.objects.filter(test=test)

    if not (has_attempted_test(user_profile, test) or is_user_owner_of_test(user_profile, test)):
        return build_repsonse_with_message("Not found",
                                           response_status=status.HTTP_404_NOT_FOUND)

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


@api_view(["GET", "POST"])
@rest_login_required_or_404
@wrap_with_internal_service_exception
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
@rest_login_required_or_404
@wrap_with_internal_service_exception
def bulk_upload(request, pk):
    user_profile = get_object_or_404_status_response(UserProfile, user__user=request.user)
    test = get_object_or_404_status_response(Test, pk=pk, owner=user_profile, publish=False)

    try:
        uploaded_file = request.FILES["csv_file"]
    except MultiValueDictKeyError:
        return build_repsonse_with_message("File not found", status.HTTP_400_BAD_REQUEST)

    uploaded_file_type = get_file_type(uploaded_file)

    if uploaded_file_type == "csv":
        question_list = get_data_from_csv(uploaded_file)
    elif uploaded_file_type in ["xls", "xlsx"]:
        question_list = get_data_from_excel(uploaded_file, column_limit=5, sheet_name='questions')
    else:
        return build_repsonse_with_message("File type not supported", status.HTTP_400_BAD_REQUEST)

    # check each row has 5 columns for question and 4 options, ignore blank rows
    questions = []
    valid = True
    for question in question_list:
        if not len(question) in [0, 5]:
            valid = False
            break
        elif len(question) == 5:
            questions.append(question)

    if not valid:
        return build_repsonse_with_message("File not in expected format", status.HTTP_400_BAD_REQUEST)

    try:
        for question in questions:
            Question.objects.create(
                question=question[0],
                wrong_answer_1=question[1],
                wrong_answer_2=question[2],
                wrong_answer_3=question[3],
                correct_answer=question[4],
                test=test,
            )
    except ValidationError as e:
        return build_repsonse_with_message(e.message, status.HTTP_412_PRECONDITION_FAILED)

    return build_repsonse_with_message("Questions uploaded", status.HTTP_201_CREATED)
