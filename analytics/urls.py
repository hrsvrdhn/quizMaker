from django.urls import re_path
from analytics import views

urlpatterns = [
	re_path(r'^$', views.analytics_page, name="home"),
	re_path(r'^download$', views.analytics_download, name="download"),
]