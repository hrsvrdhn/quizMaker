from django import forms
from .models import UserProfile
from quiz.models import Test

class EmailTestForm(forms.Form):
    users = forms.ModelMultipleChoiceField(queryset=UserProfile.objects.all())
    test = forms.ModelChoiceField(queryset=Test.objects.filter(publish=True, is_active=True))
    