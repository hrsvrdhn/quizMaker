import random
import string
import csv
from threading import Thread

import sendgrid
from django.conf import settings
from django.template import loader
from django.utils.text import slugify
from rest_framework import status
from rest_framework.response import Response
from pyexcel_xls import get_data as xls_get
from pyexcel_xlsx import get_data as xlsx_get


def postpone(function):
    def decorator(*args, **kwargs):
        try:
            t = Thread(target=function, args=args, kwargs=kwargs)
            t.daemon = True
            t.start()
        except:
            pass

    return decorator


def rest_login_required_or_404(function):
    def decorator(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return function(request, *args, **kwargs)

    return decorator


def random_string_generator(size=10, chars=string.ascii_lowercase + string.digits):
    return "".join(random.choice(chars) for _ in range(size))


def unique_slug_generator(instance, new_slug=None):
    if new_slug is not None:
        slug = new_slug
    else:
        slug = slugify(instance.title)

    Klass = instance.__class__
    qs_exists = Klass.objects.filter(slug=slug).exists()
    if qs_exists:
        new_slug = "{slug}-{randstr}".format(
            slug=slug, randstr=random_string_generator(size=4)
        )
        return unique_slug_generator(instance, new_slug=new_slug)
    return slug


def random_key_generator(size=10, digits="0987654321"):
    return "".join(random.choice(digits) for _ in range(size))


@postpone
def feedback_mail(feedback):
    html_message = loader.render_to_string(
        "testFeedbackMessage.html",
        {
            "test_name": feedback.test.name,
            "candidate_name": feedback.candidate.user.user.get_full_name(),
            "rating": feedback.rating,
            "message": feedback.message,
        },
    )
    email_address = feedback.test.owner.user.user.email
    if not email_address:
        return
    print(email_address)
    sg = sendgrid.SendGridAPIClient(apikey=getattr(settings, "SENDGRID_API_KEY", ""))
    mail = {
        "personalizations": [
            {"to": [{"email": email_address}], "subject": "Your Quiz Feedback"}
        ],
        "from": {
            "name": "QuizMaker",
            "email": getattr(settings, "DEFAULT_ADMIN_EMAIL", "no-reply@quizmaker.com"),
        },
        "content": [{"type": "text/html", "value": html_message}],
    }
    response = sg.client.mail.send.post(request_body=mail)
    if response.status_code == 202:
        print("Email sent to admin")
    else:
        print("Error sending email")


@postpone
def send_test_complete_email(teststat):
    html_message = loader.render_to_string(
        "testCompletedMessage.html",
        {
            "test_name": teststat.test.name,
            "candidate_name": teststat.candidate.user.user.get_full_name(),
            "test_score": teststat.score,
        },
    )
    email_address = teststat.candidate.user.user.email
    if not email_address:
        return
    print(email_address)
    sg = sendgrid.SendGridAPIClient(apikey=getattr(settings, "SENDGRID_API_KEY", ""))
    mail = {
        "personalizations": [
            {"to": [{"email": email_address}], "subject": "Scorecard"}
        ],
        "from": {
            "name": "QuizMaker",
            "email": getattr(settings, "DEFAULT_ADMIN_EMAIL", "no-reply@quizmaker.com"),
        },
        "content": [{"type": "text/html", "value": html_message}],
    }
    response = sg.client.mail.send.post(request_body=mail)
    if response.status_code == 202:
        print("Email sent")
    else:
        print("Error sending email")


def default_difficulty():
    from quiz.models import Test

    for test in Test.objects.all():
        question_count = test.questions.count()
        test_total_percentage = 0
        total_attempts = 0

        for attempt in test.attempts.all():
            if not attempt.has_completed:
                continue
            total_attempts += 1
            test_total_percentage += float(attempt.score) / question_count

        if total_attempts == 0:
            continue

        average_percentage = (test_total_percentage * 100) / total_attempts

        if average_percentage <= 30:
            test.difficulty = 'HARD'
        elif average_percentage <= 80:
            test.difficulty = 'MEDIUM'
        else:
            test.difficulty = 'EASY'

        test.save()


def get_file_type(filename):
    return str(filename).split(".")[-1].lower()


def get_data_from_csv(file):
    return csv.reader(file.read().decode(), delimiter=',')


def get_data_from_excel(file, column_limit, sheet_name):
    if get_file_type(file) == 'xls':
        data = xls_get(file, column_limit=column_limit)
    else:
        data = xlsx_get(file, column_limit=column_limit)

    return data.get(sheet_name, [])
