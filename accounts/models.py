import sendgrid, bleach

from django.db import models
from django.dispatch import receiver
from django.urls import reverse_lazy
from django.conf import settings
from django.db.models import Sum

from allauth.account.signals import user_logged_in
from allauth.socialaccount.models import SocialAccount

from topic.models import Topic
# Create your models here.
class UserProfileManager(models.Manager):
    use_for_related_fields = True

    def all(self):
        qs = self.get_queryset().all()
        try:
            if self.instance:
                qs = qs.exclude(user=self.instance)
        except:
            pass
        return qs

    def toggle_follow(self, user, to_toggle_user):
        user_profile = UserProfile.objects.get(user__user=user)
        if to_toggle_user in user_profile.following.all():
            user_profile.following.remove(to_toggle_user)
            added = False
        else:
            user_profile.following.add(to_toggle_user)
            added = True
        return added

    def is_following(self, user, target_user):
        if not isinstance(user, UserProfile) or not isinstance(user, UserProfile):
            return NotImplementedError
        if target_user in user.following.all():
            return True
        return False

class UserProfile(models.Model):
    user = models.OneToOneField(SocialAccount, related_name='profile', on_delete=models.CASCADE)
    following = models.ManyToManyField('self', blank=True, symmetrical=False, related_name='followed_by')
    topics = models.ManyToManyField(Topic, blank=True, related_name='liked_by')
    profilepic_url = models.CharField(max_length=1000, blank=True)

    objects = UserProfileManager()
    
    def __str__(self):
        return str(self.user.user.username)
    
    def get_following(self):
        users  = self.following.all() # User.objects.all().exclude(username=self.user.username)
        return users.exclude(username=self.user.username)

    def get_follow_url(self):
        return reverse_lazy("user:follow", kwargs={"username":self.user.user.username})

    def get_absolute_url(self):
        return reverse_lazy("user:profile", kwargs={"username":self.user.user.username})
    
    def get_total_tests_taken(self):
        return self.teststats.filter(candidate=self, has_completed=True).count()

    def get_attempts_count(self):
        ans = 0
        for result in self.teststats.filter(has_completed=True):
            ans += result.test.get_question_count()
        return ans
    
    def get_correct_response_count(self):
        return self.teststats.filter(has_completed=True).aggregate(Sum('score')).get("score__sum")
    
    def get_wrong_response_count(self):
        ans = 0
        for result in self.teststats.filter(has_completed=True):
            ans += result.get_wrong_response_count()
        return ans
    
    def get_accuracy(self):
        try:
            return round(self.get_correct_response_count() / self.get_attempts_count(),2)
        except:
            return None


class WebFeedback(models.Model):
    name = models.CharField(max_length=250)
    email = models.EmailField(max_length=250)
    description = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{}".format(self.name)

    def save(self, *args, **kwargs):
        self.name = bleach.clean(self.name)
        self.description = bleach.clean(self.description)        
        super(WebFeedback, self).save(*args, **kwargs)
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
                "name": self.name,
                "email": self.email,
            },
            "content": [
                {
                    "type": "text/html",
                    "value": "<p>Name: {}</p><p>Email: {}</p><p>Description: {}</p>".format(self.name, self.email, self.description)
                }
            ]
        }
        response = sg.client.mail.send.post(request_body=mail)
        if response.status_code == 202:				
            print("Email sent to admin")
        else:
            print("Error sending email")
    

# SIGNALS 
@receiver(user_logged_in)
def user_logged_in(request, user, *args, **kwargs):
    new_user, created = UserProfile.objects.get_or_create(user=SocialAccount.objects.get(user=user))
    if created:
        print("New user")
    else:
        print("old user")