from django.urls import re_path
from accounts import views

urlpatterns = [
    re_path(r'^$', views.myProfile, name='myprofile'),
    re_path(r'^(?P<username>[\w.@+-]+)/$', views.Profile, name='profile'),
    re_path(r'^(?P<username>[\w.@+-]+)/follow$', views.UserFollowView, name='follow'),
    re_path(r'^feedback$', views.WebsiteFeedback, name='websiteFeedback'),  
    re_path(r'^topscorers$', views.TopScorers, name='topscorers'),          
]