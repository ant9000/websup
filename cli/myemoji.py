from django_imports import escape, escapejs
from os import path
import binascii
import emoji

EMOJI_STATIC_ROOT = path.join(path.dirname(emoji.__file__), 'static', 'emoji')


def image_data_uri(self, filename, alt=None):
    title = ' '.join(filename.split('_'))
    image = open(path.join(EMOJI_STATIC_ROOT, 'img', filename + '.png')).read()
    return '<img src="data:%s;base64,%s" ' \
        'alt="%s" title="%s" width="24" height="24" />' % (
            'image/png',
            binascii.b2a_base64(image).strip(),
            alt or title,
            title,
        )


def replace(s, as_data_uri=True):
    old = emoji.models.Emoji._image_string
    if as_data_uri:
        emoji.models.Emoji._image_string = image_data_uri
    out = emoji.models.Emoji.replace_unicode(s)
    emoji.models.Emoji._image_string = old
    return out


if __name__ == '__main__':
    print replace(u'\u2049', as_data_uri=False)
    print replace(u'\u2049')
