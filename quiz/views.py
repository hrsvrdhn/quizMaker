from random import shuffle
import bleach, re, requests

from django.shortcuts import render, HttpResponse, get_object_or_404, HttpResponseRedirect, HttpResponsePermanentRedirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.core import serializers
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_http_methods
from django.utils.html import escape
from django.utils import timezone

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from accounts.models import UserProfile
from topic.models import Topic
from .forms import AddQuizForm, AddTestForm
from .models import Test, Question, TestStat, QuestionStat, Feedback
from .serializers import TestSerializer, QuestionSerializer, QuestionListSerializer, QuestionStatSerializer, CorrectAnswerSerialize, TestSerializerForHome

def home(request):
	print("Home")
	user_context = None
	if request.user.is_authenticated:
		user_profile = get_object_or_404(UserProfile, user__user=request.user)
		try:
			pic_url = requests.get(user_profile.user.get_avatar_url()).url
		except:
			pic_url = None
		user_context =  {
			'name': user_profile.user.extra_data['name'],
			'profile_pic': pic_url,
			'pageTitle': 'Home', 
		}
	return render(request, "home.html", {'user_context': user_context})

@login_required
def myTest(request):
	print("My Test")
	user_profile = get_object_or_404(UserProfile, user__user=request.user)	
	tests = Test.objects.filter(owner=user_profile)
	form = AddTestForm()
	try:
		pic_url = requests.get(user_profile.user.get_avatar_url()).url
	except:
		pic_url = None
	user_context =  {
		'name': user_profile.user.extra_data['name'],
		'profile_pic': pic_url,
		'pageTitle': 'My test', 
	}
	return render(request, "mytest.html", {'tests': tests, 'testForm': form, 'user_context': user_context})

@login_required
@api_view(['POST'])
def addTestForm(request):
	print('Add test form')
	user_profile = get_object_or_404(UserProfile, user__user=request.user)	
	serializer = TestSerializer(data=request.data)
	if serializer.is_valid():
		print(serializer.validated_data)
		serializer.save(owner=user_profile)
		return Response(serializer.data, status=status.HTTP_201_CREATED)
	return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@login_required
def manageTest(request, pk=None):
	print("ManageTest")
	qform = AddQuizForm()
	user_profile = get_object_or_404(UserProfile, user__user=request.user)	
	if request.method == "POST":
		pass
	else:
		test = get_object_or_404(Test, pk=pk, owner=user_profile)
		questions = test.questions.all()
		all_topics = Topic.objects.exclude(tests=test)
		try:
			pic_url = requests.get(user_profile.user.get_avatar_url()).url
		except:
			pic_url = None
		user_context =  {
			'name': user_profile.user.extra_data['name'],
			'profile_pic': pic_url,
			'pageTitle': 'Manage Test', 
		}
		return render(request, 'manageTest.html', { 'all_topics': all_topics, 'qform': qform, 'test': test, 'user_context': user_context})
		
@login_required
@api_view(['GET','PUT','DELETE'])
def updateQuestionForm(request, tpk=None, qpk=None):
	print("Hellllllllllllllooooooooo", request.method)
	user_profile = get_object_or_404(UserProfile, user__user=request.user)	
	try:
		test = Test.objects.get(pk=tpk, owner=user_profile)
		question = Question.objects.get(pk=qpk, test=test)
	except (Question.DoesNotExist, Test.DoesNotExist) as exceptions:
		return Response(status=status.HTTP_404_NOT_FOUND)
	if request.method == 'GET':
		serializer = QuestionSerializer(question)
		return Response(serializer.data)
	elif request.method == 'PUT':
		if test.publish:
			raise Http404
		print(request.data)
		serializer = QuestionSerializer(question , data=request.data)
		if serializer.is_valid():
			print(serializer.validated_data)
			serializer.save()
			questions = Test.objects.get(pk=tpk, owner=user_profile).questions.all()
			serializer = QuestionListSerializer(questions, many=True)
			return Response(serializer.data)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
	elif request.method == 'DELETE':
		if test.publish:
			raise Http404
		question.delete()
		questions = Test.objects.get(pk=tpk, owner=user_profile).questions.all()	
		serializer = QuestionListSerializer(questions, many=True)
		return Response(serializer.data)

@login_required
@api_view(['POST'])
def addQuestionForm(request, pk):
	user_profile = get_object_or_404(UserProfile, user__user=request.user)		
	try:
		test = Test.objects.get(pk=pk, owner=user_profile)
	except Test.DoesNotExist:
		return Response(status=status.HTTP_404_NOT_FOUND)
	if test.publish:
		raise Http404
	serializer = QuestionSerializer(data=request.data)
	if serializer.is_valid():
		print(serializer.validated_data)
		serializer.save(test=test)
		questions = Question.objects.filter(test=Test.objects.get(pk=pk, owner=user_profile))
		serializer = QuestionListSerializer(questions, many=True)
		return Response(serializer.data)
	return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@login_required
@api_view(['GET'])
def getQuestionList(request, pk):
	user_profile = get_object_or_404(UserProfile, user__user=request.user)
	try:
		test = Test.objects.get(pk=pk)
		questions = Question.objects.filter(test=test)
	except:
		return Response(status=status.HTTP_404_NOT_FOUND)
	if user_profile == test.owner or TestStat.objects.filter(test=test, candidate=user_profile).exists():
		serializer = QuestionListSerializer(questions, many=True)
		for data in serializer.data:
			# data['question'] = re.sub("<.*?>", " ", data['question'])
			# data['question'] = bleach.clean(data['question'])
			optionList = [data['option1'], data['option2'], data['option3'], data['option4']]
			shuffle(optionList)
			i = 0
			while i < 4:
				data['option'+str(i+1)] = bleach.clean(optionList[i])
				i += 1
		return Response(serializer.data)
	return Response(status=status.HTTP_404_NOT_FOUND)

@login_required
@api_view(['GET', 'POST'])
def QuestionStatForm(request, qpk):
	question = get_object_or_404(Question, pk=qpk)
	user_profile = get_object_or_404(UserProfile, user__user=request.user)	
	teststat = get_object_or_404(TestStat, test=question.test, candidate=user_profile)
	if request.method == "GET":
		try:
			questionstat, create = QuestionStat.objects.get_or_create(question=question, candidate=user_profile)
			if teststat.has_completed:
				questionstat.correct_answer = question.correct_answer
			serializer = QuestionStatSerializer(questionstat)
			return Response(serializer.data)
		except Exception as e:
			print(e)
			return Response()
	else:
		user_response = request.POST['option']
		if not user_response or teststat.has_completed:
			return Response(status=HTTP_400_BAD_REQUEST)
		questionstat, created = QuestionStat.objects.get_or_create(question=question, candidate=user_profile)
		questionstat.response = user_response
		questionstat.save()
		return Response(status=status.HTTP_201_CREATED)

@login_required
def takeQuiz(request, pk):
	test = get_object_or_404(Test, pk=pk)
	user_profile = get_object_or_404(UserProfile, user__user=request.user)	
	if test.owner == user_profile:
		return HttpResponseRedirect(reverse('quiz:manageTest', args=[pk]))
	if not test.publish or (not test.is_active and not test.attempts.filter(candidate=user_profile).exists()):
		raise Http404
	teststat, created = TestStat.objects.get_or_create(test=test, candidate=user_profile)
	has_completed = teststat.has_completed	
	no_of_questions = Question.objects.filter(test=test).count()
	score = teststat.score
	try:
		feedback = Feedback.objects.get(test=test, candidate=user_profile)
		feedback = feedback.rating
	except Feedback.DoesNotExist:
		feedback = None
	try:
		pic_url = requests.get(user_profile.user.get_avatar_url()).url
	except:
		pic_url = None
	user_context =  {
		'name': user_profile.user.extra_data['name'],
		'profile_pic': pic_url,
		'pageTitle': test.name, 
	}
	context = {
		'testno': test.id,
		'score': score,	
		'has_completed': has_completed,
		'no_of_questions': range(no_of_questions),
		'feedback': feedback,
		'user_context': user_context,
	}
	return render(request, 'quizDashboard.html', context)

@login_required
@require_http_methods(['POST'])
def endQuiz(request, pk):
	test = get_object_or_404(Test, pk=pk)
	user_profile = get_object_or_404(UserProfile, user__user=request.user)	
	if test.owner == request.user.username:
		return HttpResponseRedirect(reverse('quiz:manageTest', args=[pk]))
	teststat = get_object_or_404(TestStat, test=test, candidate=user_profile)
	teststat.has_completed = True
	teststat.save()
	return HttpResponsePermanentRedirect(reverse('quiz:takeQuiz', args=[pk]))

from topic.serializers import TopicSerializer
@api_view(['POST'])
def AddTopic(request, pk):
	if request.user.is_authenticated:
		user_profile = get_object_or_404(UserProfile, user__user=request.user)		
		test = get_object_or_404(Test, pk=pk, owner=user_profile)
		serializer = TopicSerializer(data=request.data)
		if serializer.is_valid() and test.topics.count() < 10:
			if serializer.validated_data['name'].isalnum():
				topic, created = Topic.objects.get_or_create(name=serializer.validated_data['name'])
				test.topics.add(topic)
				return Response(serializer.data, status=status.HTTP_200_OK)
	return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
def DeleteTopic(request, pk):
	if request.user.is_authenticated:
		user_profile = get_object_or_404(UserProfile, user__user=request.user)		
		serializer = TopicSerializer(data=request.data)
		if serializer.is_valid():
			topic = get_object_or_404(Topic, name=serializer.validated_data['name'])
			test = get_object_or_404(Test, pk=pk, owner=user_profile)			
			test.topics.remove(topic)
			return Response(status=status.HTTP_200_OK)        
	return Response(status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
def ToggleTestPublish(request, pk):
	if request.user.is_authenticated:
		user_profile = get_object_or_404(UserProfile, user__user=request.user)
		test = get_object_or_404(Test, pk=pk, owner=user_profile)
		if test.questions.count() == 0:
			return Response({'message': "Empty question list"}, status=status.HTTP_400_BAD_REQUEST)
		test.publish = True
		test.is_active = True
		test.published_on = timezone.now()
		test.save()
		return Response({'published':test.publish}, status=status.HTTP_200_OK)
	return Response(status=status.HTTP_404_NOT_FOUND)
		
@api_view(['PUT'])
def ToggleTestActive(request, pk):
	if request.user.is_authenticated:
		user_profile = get_object_or_404(UserProfile, user__user=request.user)
		test = get_object_or_404(Test, pk=pk, owner=user_profile)	
		if test.publish:
			test.is_active = not test.is_active
			test.save()
			return Response({'active':test.is_active}, status=status.HTTP_200_OK)
	return Response(status=status.HTTP_404_NOT_FOUND)

def testDetail(request, pk):
	test = get_object_or_404(Test, publish=True, pk=pk)
	teststats = TestStat.objects.filter(test=test, has_completed=True).order_by('-score')
	context = {
		'test': test,
		'teststats': teststats,
	}
	if request.user.is_authenticated:
		user_profile = get_object_or_404(UserProfile, user__user=request.user)
		try:
			user_teststat = TestStat.objects.get(test=test, candidate=user_profile)
		except:
			user_teststat = None
		try:
			pic_url = requests.get(user_profile.user.get_avatar_url()).url
		except:
			pic_url = None
		context['user_teststat'] = user_teststat
		user_context =  {
			'name': user_profile.user.extra_data['name'],
			'profile_pic': pic_url,
			'pageTitle': test.name,
		}
		context['user_context'] = user_context
	return render(request, 'testDetail.html', context)

@login_required
@api_view(['POST'])
def testFeedback(request, pk):
	test = get_object_or_404(Test, publish=True, pk=pk)
	user_profile = get_object_or_404(UserProfile, user__user=request.user)
	teststat = get_object_or_404(TestStat, test=test, candidate=user_profile, has_completed=True)
	if not Feedback.objects.filter(test=test, candidate=user_profile).exists():
		try:
			rating_int = int(request.POST.get('rating'))
			if rating_int >= 0 and rating_int <=5:
				feedback = Feedback.objects.create(test=test, candidate=user_profile, rating=rating_int)
				return Response(status=status.HTTP_201_CREATED)
		except:
			pass
	return Response(status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def RecommendedTest(request):
	if request.user.is_authenticated:
		user_profile = get_object_or_404(UserProfile, user__user=request.user)
		recommeded_tests = sorted(Test.objects.recommended(user_profile), key=lambda x:x.get_average_rating, reverse=True)
		serializer = TestSerializerForHome(recommeded_tests, many=True)
		return Response(serializer.data, status=status.HTTP_200_OK)
	return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def MostPopularTest(request):
	if request.user.is_authenticated:
		user_profile = get_object_or_404(UserProfile, user__user=request.user)		
		most_popular = sorted(Test.objects.exclude(owner=user_profile).filter(publish=True, is_active=True), key=lambda x:x.get_attempts(), reverse=True)[:5]
	else:
		most_popular = sorted(Test.objects.filter(publish=True, is_active=True), key=lambda x:x.get_attempts(), reverse=True)[:5]
	serializer = TestSerializerForHome(most_popular, many=True)
	return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def NewTest(request):
	if request.user.is_authenticated:
		user_profile = get_object_or_404(UserProfile, user__user=request.user)
		new_tests = Test.objects.exclude(owner=user_profile).filter(publish=True, is_active=True).order_by("-created_on")[:5]
	else:
		new_tests = Test.objects.filter(publish=True, is_active=True).order_by("-created_on")[:5]
	serializer = TestSerializerForHome(new_tests, many=True)
	return Response(serializer.data, status=status.HTTP_200_OK)
	
@api_view(['GET'])
def score_distribution(requests, pk):
	test = get_object_or_404(Test, pk=pk)
	teststats = TestStat.objects.filter(test=test, has_completed=True)
	percentage = 0.2
	data = []
	data.append(teststats.filter(score__gte=(percentage-0.2)*test.get_question_count(),score__lte=percentage*test.get_question_count()).count())
	percentage += 0.2
	while percentage <= 1:
		data.append(teststats.filter(score__gt=(percentage-0.2)*test.get_question_count(),score__lte=percentage*test.get_question_count()).count())
		percentage += 0.2
	return Response({"data": data})

@require_http_methods(['GET'])
def allTests(request):
	topic = request.GET.get("topic", None)
	topics = Topic.objects.all()
	tests = Test.objects.filter(publish=True, is_active=True)
	context = {
		'topic': topic,
		"topics": topics,
		"tests": tests, 
	}
	return render(request, "alltest.html", context)
