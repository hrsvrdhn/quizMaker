"""quizmaker URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.urls import re_path, include
from django.contrib import admin
from django.views.generic import RedirectView

from accounts.views import NotFound

urlpatterns = [
    re_path(r"^accounts/social/signup", NotFound),
    re_path(
        r"^accounts\/(signup/*|password\S*|inactive/*|(confirm-){0,1}email\S*|password\S*)$",
        NotFound,
    ),
    re_path(r"^adminhere/", admin.site.urls),
    re_path(r"^accounts/", include("allauth.urls")),
    re_path(r"^quiz/", include(("quiz.urls", "quiz"))),
    re_path(r"^user/", include(("accounts.urls", "user"))),
    re_path(r"^topic/", include(("topic.urls", "topic"))),
    re_path(r"^analytics/", include(("analytics.urls", "analytics"))),
    re_path(r"^$", RedirectView.as_view(url="/quiz")),
]

handler404 = "accounts.views.NotFound"
handler500 = "accounts.views.ServerError"
handler400 = "accounts.views.BadRequest"


admin.site.site_header = "QuizMaker Administration"
admin.site.site_title = "QuizMaker Admin Portal"
admin.site.index_title = "Welcome Administrator"
