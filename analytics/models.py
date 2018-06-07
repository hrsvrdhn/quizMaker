from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.dispatch import receiver
from django.contrib.sessions.models import Session

from allauth.account.signals import user_logged_in, user_logged_out

from accounts.models import UserProfile

from .signals import object_viewed_signal
from .utils import get_client_ip
# Create your models here.

class ObjectViewed(models.Model):
	user = models.ForeignKey(UserProfile, blank=True, null=True, on_delete=models.SET_NULL)
	ip_address = models.CharField(max_length=200, blank=True, null=True)
	content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE) # Take any model
	object_id = models.PositiveIntegerField() # Primary Key of that object
	content_object = GenericForeignKey('content_type', 'object_id') # Any Object Instance
	#url
	timestamp = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return "{} viewed on {}".format(self.content_object, self.timestamp)

	class Meta:
		ordering = ['-timestamp']
		verbose_name = 'Object viewed'
		verbose_name_plural = 'Objects viewed'


@receiver(object_viewed_signal)
def object_viewed_signal(sender, instance, request, *args, **kwargs):
	print(sender, instance, request)
	c_type = ContentType.objects.get_for_model(sender)
	try:
		user_profile = UserProfile.objects.get(user__user=request.user)
	except:
		user_profile = None
	new_obj_viewed = ObjectViewed.objects.create(
			user = user_profile,
			ip_address = get_client_ip(request),
			content_type = c_type,
			object_id = instance.id
		)


class UserSession(models.Model):
	user = models.ForeignKey(UserProfile, blank=True, null=True, on_delete=models.SET_NULL)
	ip_address = models.CharField(max_length=200, blank=True, null=True)
	session_key = models.CharField(max_length=100, blank=True, null=True)
	timestamp = models.DateTimeField(auto_now_add=True)
	active = models.BooleanField(default=True)
	ended = models.BooleanField(default=False)

	def __str__(self):
		return "{} session from {}".format(self.user.user.user.get_full_name(), self.ip_address)

	def end_session(self):
		session_key = self.session_key
		ended = self.ended
		try:
			Session.objects.get(pk=session_key).delete()
			self.active = False
			self.ended = True
			self.save()
		except:
			pass
		return self.ended	

@receiver(user_logged_in)
def user_logged_in(request, user, *args, **kwargs):
	try:
		user_profile = UserProfile.objects.get(user__user=request.user)
		ip_address = get_client_ip(request)
		session_key = request.session.session_key
		print(session_key)
		UserSession.objects.create(
				user = user_profile,
				ip_address = ip_address,
				session_key = session_key
			)
	except Exception as e:
		print("Exception occured while user_logged_in", e)


@receiver(user_logged_out)
def user_logged_out(request, user, *args, **kwargs):
	try:
		session_key = request.session.session_key
		user_profile = UserProfile.objects.get(user__user=request.user)
		ip_address = get_client_ip(request)
		user_session_obj = UserSession.objects.get(user=user_profile, session_key=session_key)
		user_session_obj.end_session()
	except Exception as e:
		print("Exception occured while user_logged_out", e)