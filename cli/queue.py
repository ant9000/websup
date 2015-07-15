from gevent.queue import Queue
import json


class QueueItem:
    def __init__(self, item_type, content):
        self.item_type = item_type
        self.content = content

    def __str__(self):
        return '%s: %s' % (self.item_type, self.content)

    def asJson(self):
        try:
            js = json.dumps({'type': self.item_type, 'content': self.content})
        except TypeError:
            js = json.dumps(
                {'type': self.item_type, 'content': '%s' % self.content}
            )
        return js
