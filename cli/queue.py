from gevent.queue import Queue
from datetime import datetime
import time


class QueueItem:
    def __init__(
        self, timestamp=None, text=None, url=None,
        thumb=None, number=None, notify=None, data=None,
        own=False,
    ):
        self.timestamp = timestamp or int(time.time())
        self.datetime = datetime.fromtimestamp(self.timestamp)
        self.text = text
        self.url = url
        self.thumb = thumb
        self.number = number
        self.notify = notify
        self.own = own
        self.data = data

    def __str__(self):
        out = self.text
        if self.number:
            out = '%s: %s' % (self.number, out)
        return out

    def asDict(self):
        return {
            'timestamp': self.timestamp,
            'number': self.number,
            'notify': self.notify,
            'text': self.text,
            'url': self.url,
            'thumb': self.thumb,
            'own': self.own,
        }
