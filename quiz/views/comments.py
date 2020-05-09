from django.http import Http404
from django.shortcuts import (
    get_object_or_404,
    HttpResponsePermanentRedirect,
)
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from accounts.models import UserProfile
from quiz.models import Test, Comment
from quiz.views import get_object_or_404_status_response


@api_view(["POST"])
def add_comment(request, pk):
    message = request.POST.get("message", None)
    if not message:
        return Response(
            {"message": "Comment cannot be empty"}, status=status.HTTP_400_BAD_REQUEST
        )
    user_profile = get_object_or_404_status_response(UserProfile, user__user=request.user)
    test = get_object_or_404_status_response(Test, pk=pk)

    Comment.objects.create(candidate=user_profile, test=test, message=message)
    return Response({"data": "Comment added"})


@api_view(["GET"])
def delete_comment(request, pk, cpk):
    user_profile = get_object_or_404(UserProfile, user__user=request.user)
    test = get_object_or_404(Test, pk=pk)
    comment = get_object_or_404(Comment, test=test, pk=cpk)
    # only test owner and comment author can delete the comment
    if not test.owner == user_profile and not comment.candidate == user_profile:
        raise Http404
    comment.delete()
    return HttpResponsePermanentRedirect(test.get_test_detail_url())
