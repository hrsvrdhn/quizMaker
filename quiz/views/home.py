from django.shortcuts import render

from quiz.constants import PageTitle
from quiz.views.common_view_utils import build_user_context


def home(request):
    user_context = build_user_context(request.user, PageTitle.HOME)
    return render(request, "home.html", {"user_context": user_context})