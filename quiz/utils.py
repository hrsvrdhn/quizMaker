import random
import string
import sendgrid

from django.template import loader
from django.conf import settings
from django.utils.text import slugify

def random_string_generator(size=10, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def unique_slug_generator(instance, new_slug=None):
    if new_slug is not None:
        slug = new_slug
    else:
        slug = slugify(instance.title)

    Klass = instance.__class__
    qs_exists = Klass.objects.filter(slug=slug).exists()
    if qs_exists:
        new_slug = "{slug}-{randstr}".format(
                    slug=slug,
                    randstr=random_string_generator(size=4)
                )
        return unique_slug_generator(instance, new_slug=new_slug)
    return slug

def random_key_generator(size=10, digits='0987654321'):
    return ''.join(random.choice(digits) for _ in range(size))


def feedback_mail(feedback):
    html_message = loader.render_to_string(
            'testFeedbackMessage.html',
            {
                'test_name': feedback.test.name,
                'candidate_name': feedback.candidate.user.user.get_full_name(),
                'rating': feedback.rating,
                'message': feedback.message,
            }                        
        )
    email_address = feedback.test.owner.user.user.email
    if not email_address:
        return
    print(email_address)
    sg = sendgrid.SendGridAPIClient(apikey=getattr(settings, "SENDGRID_API_KEY", ""))
    mail = {
        "personalizations": [
            {
                "to": [
                {
                    "email": email_address,
                },
                ],
                "subject": "Your Quiz Feedback"
            }
        ],
        "from": {
            "name": "QuizMaker",
            "email": getattr(settings, "DEFAULT_ADMIN_EMAIL", "no-reply@quizmaker.com"),
        },
        "content": [
            {
                "type": "text/html",
                "value": html_message
            }
        ]
    }
    response = sg.client.mail.send.post(request_body=mail)
    if response.status_code == 202:             
        print("Email sent to admin")
    else:
        print("Error sending email")