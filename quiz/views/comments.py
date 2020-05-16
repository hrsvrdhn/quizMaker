from django.http import Http404
from django.shortcuts import HttpResponsePermanentRedirect
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from accounts.models import UserProfile
from quiz.models import Test, Comment
from quiz.views.common_view_utils import get_object_or_404_status_response, build_repsonse_with_message


@api_view(["POST"])
def add_comment(request, pk):
    message = request.POST.get("message", None)
    if not message:
        return build_repsonse_with_message("Comment cannot be empty", response_status=status.HTTP_400_BAD_REQUEST)

    user_profile = get_object_or_404_status_response(UserProfile, user__user=request.user)
    test = get_object_or_404_status_response(Test, pk=pk)

    Comment.objects.create(candidate=user_profile, test=test, message=message)
    return Response()


@api_view(["GET"])
def delete_comment(request, user_pk, comment_pk):
    user_profile = get_object_or_404_status_response(UserProfile, user__user=request.user)
    test = get_object_or_404_status_response(Test, pk=user_pk)
    comment = get_object_or_404_status_response(Comment, test=test, pk=comment_pk)
    # only test owner and comment author can delete the comment
    if not (test.owner == user_profile or comment.candidate == user_profile):
        raise Http404
    comment.delete()
    return HttpResponsePermanentRedirect(test.get_test_detail_url())
