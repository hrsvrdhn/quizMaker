from secrets import compare_digest

from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from accounts.models import UserProfile
from quiz.models import TestStat
from quiz.utils import send_test_complete_email


def get_object_or_404_status_response(klass, *args, **kwargs):
    """
    Catches HTTP 404 exception and returns 404 REST response if object not found

    :param klass: Model class of required object
    :param args: non-key worded arguments
    :param kwargs: key worded arguments

    :return: Object if found else Not found REST response
    """
    try:
        return get_object_or_404(klass, *args, **kwargs)
    except Http404:
        return Response(status=status.HTTP_404_NOT_FOUND)


def is_user_owner_of_test(user_profile, test):
    """
    Find whether test is owned by user
    :param user_profile: UserProfile object
    :param test: Test object
    :return: True if user owner of test else False
    """
    return user_profile == test.owner


def has_attempted_test(user_profile, test):
    """
    Find whether user has attempted test or not
    :param user_profile: UserProfile object
    :param test: Test Object
    :return: True if user attempted test otherwise False
    """
    return TestStat.objects.filter(test=test, candidate=user_profile).exists()


def get_object_or_none(klass, *args, **kwargs):
    """
    Get requested object or None

    :param klass: Model class of required object
    :param args: non-key worded arguments
    :param kwargs: key worded arguments

    :return: Object if found else None
    """
    try:
        return klass.objects.get(*args, **kwargs)
    except klass.DoesNotExist:
        return None


def can_take_quiz(test, user_profile, token):
    """
    Finds whether user can view quiz taking page or not

    :param test: Test object
    :param user_profile: UserProfile object
    :param token: Private quiz token
    :return: quiz taking eligibility
    """
    # check test is published
    result = test.publish
    # test must be active if request made to take quiz is for first time
    result &= test.is_active or test.attempts.filter(candidate=user_profile).exists()
    # verify token if test is private
    result &= not test.private or compare_digest(test.private_key, token)

    return result


def build_user_context(user, page_title):
    """
    Builds user details

    :param user - user object from request object
    :param page_title - title of the page in String

    :return - Dictionary containing user details
    """
    if not user.is_authenticated:
        return None

    user_profile = get_object_or_404(UserProfile, user__user=user)
    return {
        "name": user_profile.user.extra_data["name"],
        "profile_pic": user_profile.get_profile_pic_url(),
        "pageTitle": page_title,
    }


def perform_test_complete_operations(test_stat):
    """
    Performs all operations related to end quiz

    :param test_stat: TestStat object
    :return: None
    """
    if test_stat.has_completed:
        return
    test_stat.has_completed = True
    test_stat.save()
    send_test_complete_email(test_stat)


def build_repsonse_with_message(message, response_status=status.HTTP_200_OK):
    return Response(
        {"message": message}, status=response_status
    )


def wrap_with_internal_service_exception(function):
    def decorator(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except Exception:
            return build_repsonse_with_message("Oops! Something went wrong.", status.HTTP_500_INTERNAL_SERVER_ERROR)
    return decorator
