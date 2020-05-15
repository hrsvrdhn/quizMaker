from django import forms
from .models import Test, Question
from django.core.validators import MinValueValidator


class AddQuizForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = [
            "question",
            "wrong_answer_1",
            "wrong_answer_2",
            "wrong_answer_3",
            "correct_answer",
        ]


class AddTestForm(forms.ModelForm):
    negative_marking = forms.IntegerField(
        validators=[MinValueValidator(0)], label="Negative marking: (1/m)", min_value=0
    )

    class Meta:
        model = Test
        fields = ["name", "negative_marking"]
