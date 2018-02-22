from django.urls import re_path
from topic import views

urlpatterns = [
    re_path(r'^add$', views.AddTopic, name='add'),
    re_path(r'^delete$', views.RemoveTopic, name='delete'),    
]