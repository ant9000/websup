from gevent.queue import Queue
import json


class QueueItem:
    def __init__(self, item_type, content):
        self.item_type = item_type
        self.content = content

    def __str__(self):
        return '%s: %s' % (self.item_type, self.data) 

    def asJson(self):
        return json.dumps({ 'type': self.item_type, 'content': self.content })
