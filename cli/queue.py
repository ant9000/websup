from gevent.queue import Queue
from datetime import datetime
import time


class QueueItem:
    def __init__(
        self, timestamp=None, text=None, url=None,
        thumb=None, sender=None, notify=None, data=None,
    ):
        self.timestamp = timestamp or int(time.time())
        self.datetime = datetime.fromtimestamp(self.timestamp)
        self.text = text
        self.url = url
        self.thumb = thumb
        self.sender = sender
        self.notify = notify
        self.data = data

    def __str__(self):
        out = self.text
        if self.sender:
            out = '%s: %s' % (self.sender, out)
        return out

    def asDict(self):
        return {
            'timestamp': self.timestamp,
            'sender': self.sender,
            'notify': self.notify,
            'text': self.text,
            'url': self.url,
            'thumb': self.thumb,
        }
