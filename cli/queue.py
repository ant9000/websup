from gevent.queue import Queue


class QueueItem:
    def __init__(self, text=None, sender=None, data=None):
        self.text = text
        self.sender = sender
        self.data = data

    def __str__(self):
        out = self.text
        if self.sender:
            out = '%s: %s' % (self.sender, out)
        return out
