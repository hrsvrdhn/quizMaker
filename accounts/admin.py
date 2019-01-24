from django.contrib import admin
from .models import UserProfile, WebFeedback

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(WebFeedback)
