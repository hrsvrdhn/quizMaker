from django.conf import settings
from django import template

register = template.Library()

@register.simple_tag
def reCaptchaSiteKey():
    return getattr(settings, "GOOGLE_RECAPTCHA_SITE_KEY", None)
    