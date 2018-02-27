import bleach

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse
from django.db.models import Sum

from topic.models import Topic
from accounts.models import UserProfile
# Create your models here.
class TestManager(models.Manager):
	def recommended(self, user):
		recommended_list = []
		for test in self.get_queryset().filter(publish=True, is_active=True):
			if test.owner != user and test.topics.all().intersection(user.topics.all()).count() >= 1 and not TestStat.objects.filter(test=test, candidate=user).exists():
				recommended_list.append(test)
		return recommended_list

class Test(models.Model):
	name = models.CharField(max_length=500, blank=False, default="Sample Test")
	owner = models.ForeignKey(UserProfile, related_name='tests', null=True, on_delete=models.SET_NULL)
	topics = models.ManyToManyField(Topic, blank=True, related_name='tests')
	created_on = models.DateTimeField(auto_now_add=True)
	modified_on = models.DateTimeField(auto_now=True)
	publish = models.BooleanField(default=False)
	is_active = models.BooleanField(default=False)
	published_on = models.DateTimeField(null=True)

	objects = TestManager()

	def get_test_taking_url(self):
		return reverse('quiz:takeQuiz', args=[self.pk])

	def get_absolute_url(self):
		return reverse('quiz:manageTest', args=[self.id])
	
	def get_test_detail_url(self):
		return reverse('quiz:testDetail', args=[self.id])

	def get_average_rating(self):
		try:
			return round(self.feedbacks.aggregate(Sum('rating')).get('rating__sum') / self.feedbacks.count(),1)
		except:
			return None
	
	def get_attempts(self):
		return self.attempts.all().count()
	
	def get_question_count(self):
		return self.questions.all().count()

	def __str__(self):
		return self.name


class Question(models.Model):
	test = models.ForeignKey(Test, related_name='questions', on_delete=models.CASCADE)
	question = models.TextField(max_length=2000, blank=False)
	wrong_answer_1 = models.CharField(max_length=500, blank=False, null=False)
	wrong_answer_2 = models.CharField(max_length=500, blank=True, null=True)
	wrong_answer_3 = models.CharField(max_length=500, blank=True, null=True)
	correct_answer = models.CharField(max_length=500, blank=True, null=True)
	created_on = models.DateTimeField(auto_now_add=True)
	is_active = models.BooleanField(default=True)

	def __str__(self):
		return self.question

	def get_update_url(self):
		return reverse('quiz:updateQuestion', kwargs={'tpk':self.test.id, 'qpk': self.id})

class TestStat(models.Model):
	test = models.ForeignKey(Test, related_name="attempts", null=True, on_delete=models.SET_NULL)
	candidate = models.ForeignKey(UserProfile, related_name='teststats', on_delete=models.CASCADE)
	has_completed = models.BooleanField(default=False)
	date_taken = models.DateTimeField(auto_now_add=True)
	score = models.IntegerField(null=True)

	def get_total_attempts(self):
		return QuestionStat.objects.filter(question__in=self.test.questions.all(), candidate=self.candidate).count()
	
	def get_wrong_response_count(self):
		if self.has_completed:
			return QuestionStat.objects.filter(question__in=self.test.questions.all(), candidate=self.candidate, is_correct=False).exclude(response=None).count()
		return None
	
	def save(self, *args, **kwargs):
		if self.has_completed:
			self.score = QuestionStat.objects.filter(question__in=self.test.questions.all(), candidate=self.candidate, is_correct=True).count()
		super(TestStat, self).save(*args, **kwargs)

	def __str__(self):
		return "{}-{}".format(self.test, "Stat")

class QuestionStat(models.Model):
	question = models.ForeignKey(Question, related_name="question_history", null=True, on_delete=models.SET_NULL)
	candidate = models.ForeignKey(UserProfile, related_name='questionstat', null=True, on_delete=models.CASCADE)	
	response = models.CharField(max_length=500)
	is_correct = models.BooleanField(default=False)

	def save(self, *args, **kwargs):
		if self.response == bleach.clean(self.question.correct_answer):
			self.is_correct = True
		super(QuestionStat, self).save(*args, **kwargs)

	def __str__(self):
		return  "{}-{}".format(self.question.question, "stat")

class Feedback(models.Model):
	rating = models.IntegerField(default=0)
	test = models.ForeignKey(Test, related_name='feedbacks', on_delete=models.CASCADE)
	candidate = models.ForeignKey(UserProfile, related_name='candidate_feedback', on_delete=models.CASCADE)
	
	def __str__(self):
		return self.test.name