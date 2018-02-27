import sendgrid

from django.conf import settings

def following_email(follower_name, following_name, following_email):
    print(follower_name, following_name, following_email)
    if not (following_email and follower_name and following_email):
        return
    sg = sendgrid.SendGridAPIClient(apikey=getattr(settings, "SENDGRID_API_KEY", ""))
    mail = {
        "personalizations": [
            {
                "to": [
                {
                    "email": following_email,
                },
                ],
                "subject": "New follower"
            }
        ],
        "from": {
            "name": "QuizMaker",
            "email": "no-reply@quizmaker.herokuapp.com",
        },
        "content": [
            {
                "type": "text/html",
                "value": f'<p>Hey {following_name}, {follower_name } is now following you in QuizMaker.</p>'
            }
        ]
    }
    response = sg.client.mail.send.post(request_body=mail)
    if response.status_code == 202:				
        print("Email sent to admin")
    else:
        print("Error sending email")
    
def web_feedback_email(instance):
    sg = sendgrid.SendGridAPIClient(apikey=getattr(settings, "SENDGRID_API_KEY", ""))
    mail = {
        "personalizations": [
            {
                "to": [
                {
                    "email": getattr(settings, "DEFAULT_ADMIN_EMAIL", "no-reply@quizmaker.com"),
                },
                ],
                "subject": "QuizMaker Feedback"
            }
        ],
        "from": {
            "name": instance.name,
            "email": instance.email,
        },
        "content": [
            {
                "type": "text/html",
                "value": "<p>Name: {}</p><p>Email: {}</p><p>Description: {}</p>".format(instance.name, instance.email, instance.description)
            }
        ]
    }
    response = sg.client.mail.send.post(request_body=mail)
    if response.status_code == 202:				
        print("Email sent to admin")
    else:
        print("Error sending email")