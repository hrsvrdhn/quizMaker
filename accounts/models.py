import sendgrid, bleach

from django.db import models
from django.dispatch import receiver
from django.urls import reverse_lazy
from django.conf import settings
from django.db.models import Sum,Count

from allauth.account.signals import user_logged_in, user_signed_up
from allauth.socialaccount.models import SocialAccount

from topic.models import Topic
from .utils import web_feedback_email, new_user_signup_email
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

    def toggle_follow(self, follower, followee):
        if not isinstance(follower, UserProfile) or not isinstance(followee, UserProfile) or follower == followee:
            return NotImplementedError
        if followee in follower.following.all():
            follower.following.remove(followee)
            added = False
        else:
            follower.following.add(followee)
            added = True
        return added

    def is_following(self, follower, followee):
        if not isinstance(follower, UserProfile) or not isinstance(followee, UserProfile):
            return NotImplementedError
        if followee in follower.following.all():
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

    def get_follow_url(self):
        return reverse_lazy("user:follow", kwargs={"username":self.user.user.username})

    def get_absolute_url(self):
        return reverse_lazy("user:profile", kwargs={"username":self.user.user.username})
    
    def get_total_tests_taken(self):
        return self.teststats.filter(candidate=self, has_completed=True).count()

    def get_attempts_count(self):
        if self.teststats.filter(has_completed=True).exists():
            return self.teststats.filter(has_completed=True).annotate(questions_count=Count("test__questions")).aggregate(Sum("questions_count")).get("questions_count__sum")
        return 0

    def get_correct_response_count(self):
        return self.questionstat.filter(question__test__attempts__has_completed=True, question__test__attempts__candidate=self, is_correct=True).distinct().count()

    def get_public_correct_response_count(self):
        return self.questionstat.filter(question__test__attempts__has_completed=True, question__test__attempts__candidate=self, is_correct=True, question__test__private=False).distinct().count()        
    
    def get_wrong_response_count(self):
        return self.questionstat.filter(question__test__attempts__has_completed=True, question__test__attempts__candidate=self, is_correct=False, response__isnull=False).exclude(response__exact="").distinct().count()
    
    def get_accuracy(self):
        try:
            return round(self.get_correct_response_count()* 100 / self.get_attempts_count(),2)
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
        web_feedback_email(self)
    

# SIGNALS 

@receiver(user_logged_in)
def user_logged_in(request, user, *args, **kwargs):
    new_user, created = UserProfile.objects.get_or_create(user=SocialAccount.objects.get(user=user))
    if created:
        print("New user")
        try:
            name = request.user.get_full_name()
            email_address = request.user.email
            new_user_signup_email(name, email_address)
            print("Welcome email sent")
        except Exception as e:
            print("Exception occured", e, dir(e))        
    else:
        print("old user")