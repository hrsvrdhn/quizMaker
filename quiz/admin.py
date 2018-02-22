from django.contrib import admin

from quiz.models import Question, Test, TestStat, QuestionStat, Feedback
# Register your models here.

admin.site.register(Question)
admin.site.register(Test)
admin.site.register(TestStat)
admin.site.register(QuestionStat)
admin.site.register(Feedback)
