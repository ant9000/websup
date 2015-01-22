from django.conf import settings
settings.configure()
settings.STATIC_URL = '/static/'
from django.utils.html import escape, escapejs
import emoji
from os import path

EMOJI_STATIC_ROOT = path.join(path.dirname(emoji.__file__), 'static', 'emoji')


def replace(s):
    out = emoji.models.Emoji.replace_unicode(s)
    return out
