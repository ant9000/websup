from gevent.queue import Queue
import time


class QueueItem:
    def __init__(self, timestamp=None, text=None, sender=None, data=None):
        self.timestamp = timestamp or int(time.time())
        self.text = text
        self.sender = sender
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
            'text': self.text,
        }
