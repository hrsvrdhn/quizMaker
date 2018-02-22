from django import forms
from .models import Test, Question
from django.core.validators import MinValueValidator, MaxValueValidator

class AddQuizForm(forms.ModelForm):
	class Meta:
		model = Question
		fields = ['question', 'wrong_answer_1', 'wrong_answer_2', 'wrong_answer_3', 'correct_answer']
 	
class AddTestForm(forms.ModelForm):
	class Meta:
		model = Test
		fields = ['name']
