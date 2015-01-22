from gevent.queue import Queue
import json


class QueueItem:
    def __init__(self, timestamp=None, text=None, sender=None, data=None):
        self.timestamp = timestamp
        self.text = text
        self.sender = sender
        self.data = data

    def __str__(self):
        out = self.text
        if self.sender:
            out = '%s: %s' % (self.sender, out)
        return out

    def toJson(self):
        return json.dumps({
            'timestamp': self.timestamp,
            'sender': self.sender,
            'text': self.text,
        })
