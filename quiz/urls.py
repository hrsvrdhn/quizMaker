from django.urls import re_path
from quiz import views

urlpatterns = [
	re_path(r'^$', views.home, name="home"),
	re_path(r'^all$', views.allTests, name="alltest"),	
	re_path(r'^mytests$', views.myTest, name="mytest"),
	re_path(r'^(?P<pk>[0-9]+)$', views.manageTest, name="manageTest"),
	re_path(r'^(?P<pk>[0-9]+)/take$', views.takeQuiz, name="takeQuiz"),
	re_path(r'^(?P<pk>[0-9]+)/detail$', views.testDetail, name="testDetail"),
	re_path(r'^(?P<pk>[0-9]+)/endquiz$', views.endQuiz, name="endQuiz"),

	re_path(r'^ajax/(?P<tpk>[0-9]+)/edit/(?P<qpk>[0-9]+)$', views.updateQuestionForm, name="updateQuestion"),
	re_path(r'^ajax/(?P<pk>[0-9]+)/add$', views.addQuestionForm, name="addQuestionForm"),
	re_path(r'^ajax/add', views.addTestForm, name="addTestForm"),
	re_path(r'^ajax/(?P<pk>[0-9]+)/addtopic$', views.AddTopic, name="addtopic"),
	re_path(r'^ajax/(?P<pk>[0-9]+)/deletetopic$', views.DeleteTopic, name="deletetopic"),			
	re_path(r'^ajax/(?P<pk>[0-9]+)/questions$', views.getQuestionList, name="getQuestions"),
	re_path(r'^ajax/(?P<qpk>[0-9]+)/response$', views.QuestionStatForm, name="QuestionStatForm"),
	re_path(r'^ajax/(?P<pk>[0-9]+)/publish$', views.ToggleTestPublish, name="togglepublish"),
	re_path(r'^ajax/(?P<pk>[0-9]+)/delete$', views.deleteTest, name="deleteTest"),	
	re_path(r'^ajax/(?P<pk>[0-9]+)/activate$', views.ToggleTestActive, name="toggleactive"),
	re_path(r'^ajax/(?P<pk>[0-9]+)/private$', views.ToggleTestPrivate, name="toggleprivate"),
	re_path(r'^ajax/(?P<pk>[0-9]+)/feedback$', views.testFeedback, name="testfeedback"),
	re_path(r'^ajax/test/recommended$', views.RecommendedTest, name="recommended_list"),	
	re_path(r'^ajax/test/popular$', views.MostPopularTest, name="most_popular"),	
	re_path(r'^ajax/test/new$', views.NewTest, name="new_test"),
	re_path(r'^ajax/test/(?P<pk>[0-9]+)/score_distribution$', views.score_distribution, name="score_distribution"),
	re_path(r'^ajax/test/(?P<pk>[0-9]+)/score_chart$', views.score_chart, name="score_chart"),
	re_path(r'^ajax/test/(?P<pk>[0-9]+)/bulk_upload$', views.csv_bulk_upload, name="csv_bulk_upload"),
	re_path(r'^ajax/test/(?P<pk>[0-9]+)/add_comment$', views.addComment, name="add_comment"),
	re_path(r'^ajax/test/(?P<pk>[0-9]+)/(?P<cpk>[0-9]+)/delete_comment$', views.deleteComment, name="delete_comment"),
]	
