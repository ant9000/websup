from django.conf import settings
from django.utils.html import escape, escapejs

settings.configure()
settings.STATIC_URL = '/static/'
