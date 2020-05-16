from django.urls import re_path
from quiz import views

urlpatterns = [
    re_path(r"^$", views.home, name="home"),
    re_path(r"^all$", views.all_tests, name="alltest"),
    re_path(r"^mytests$", views.my_test, name="mytest"),
    re_path(r"^(?P<pk>[0-9]+)$", views.manage_test, name="manageTest"),
    re_path(r"^(?P<pk>[0-9]+)/take$", views.take_quiz, name="takeQuiz"),
    re_path(r"^(?P<pk>[0-9]+)/detail$", views.test_detail, name="testDetail"),
    re_path(r"^(?P<pk>[0-9]+)/endquiz$", views.end_test, name="endQuiz"),
    re_path(
        r"^ajax/(?P<tpk>[0-9]+)/edit/(?P<qpk>[0-9]+)$",
        views.update_question_form,
        name="updateQuestion",
    ),
    re_path(
        r"^ajax/(?P<pk>[0-9]+)/add$", views.add_question_form, name="addQuestionForm"
    ),
    re_path(r"^ajax/add", views.add_test_form, name="addTestForm"),
    re_path(r"^ajax/(?P<pk>[0-9]+)/addtopic$", views.add_test_topic, name="addtopic"),
    re_path(
        r"^ajax/(?P<pk>[0-9]+)/deletetopic$", views.delete_test_topic, name="deletetopic"
    ),
    re_path(
        r"^ajax/(?P<pk>[0-9]+)/questions$", views.get_question_list, name="getQuestions"
    ),
    re_path(
        r"^ajax/(?P<qpk>[0-9]+)/response$",
        views.question_stat_form,
        name="QuestionStatForm",
    ),
    re_path(
        r"^ajax/(?P<pk>[0-9]+)/publish$", views.toggle_test_publish, name="togglepublish"
    ),
    re_path(r"^ajax/(?P<pk>[0-9]+)/delete$", views.delete_test, name="deleteTest"),
    re_path(
        r"^ajax/(?P<pk>[0-9]+)/activate$", views.toggle_test_active, name="toggleactive"
    ),
    re_path(
        r"^ajax/(?P<pk>[0-9]+)/private$", views.toggle_test_private, name="toggleprivate"
    ),
    re_path(r"^ajax/(?P<pk>[0-9]+)/feedback$", views.test_feedback, name="testfeedback"),
    re_path(r"^ajax/test/recommended$", views.recommended_test, name="recommended_list"),
    re_path(r"^ajax/test/popular$", views.most_popular_test, name="most_popular"),
    re_path(r"^ajax/test/new$", views.new_test, name="new_test"),
    re_path(
        r"^ajax/test/(?P<pk>[0-9]+)/score_distribution$",
        views.score_distribution,
        name="score_distribution",
    ),
    re_path(
        r"^ajax/test/(?P<pk>[0-9]+)/score_chart$", views.score_chart, name="score_chart"
    ),
    re_path(
        r"^ajax/test/(?P<pk>[0-9]+)/bulk_upload$",
        views.bulk_upload,
        name="csv_bulk_upload",
    ),
    re_path(
        r"^ajax/test/(?P<pk>[0-9]+)/add_comment$", views.add_comment, name="add_comment"
    ),
    re_path(
        r"^ajax/test/(?P<user_pk>[0-9]+)/(?P<comment_pk>[0-9]+)/delete_comment$",
        views.delete_comment,
        name="delete_comment",
    ),
]
