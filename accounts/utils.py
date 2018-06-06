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

new_user_message = """
<p>Hi,</p>
<p>Welcome to QuizMaker, now easily create and take quizes. Here are some quick tips for new people who have recently visited QuizMaker for the first time.</p>
<ul>
<li> Go to your Profile, add favorite topics and QuizMaker will recommend you quizes based on your favorite topics right in the homepage.<li>
<li> QuizMaker believes in Data Visualization, we have pi-charts and bar-charts for various data visualization.</li>
<li> Take test, score high and see yourself in leaderboard.<li>
<li> Adding quizes are very easier, just head on to MY TESTS and add one. Have full control when to publish the quiz and when to activate it.<li>
</ul> 
"""

def new_user_signup_email(name, email_address):
    sg = sendgrid.SendGridAPIClient(apikey=getattr(settings, "SENDGRID_API_KEY", ""))
    mail = {
        "personalizations": [
            {
                "to": [
                {
                    "email": getattr(settings, "DEFAULT_ADMIN_EMAIL", "no-reply@quizmaker.com"),
                },
                ],
                "subject": "Welcome to QuizMaker"
            }
        ],
        "from": {
            "name": name,
            "email": email_address,
        },
        "content": [
            {
                "type": "text/html",
                "value": new_user_message
            }
        ]
    }
    response = sg.client.mail.send.post(request_body=mail)
    if response.status_code == 202:             
        print("Email sent to admin")
    else:
        print("Error sending email")