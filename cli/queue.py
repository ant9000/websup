from gevent.queue import Queue


class QueueItem:
    def __init__(self, text=None, sender=None, data=None):
        self.text = text
        self.sender = sender
        self.data = data

    def __unicode__(self):
        out = unicode(self.text)
        if self.sender:
            out = '%s: %s' % (unicode(self.sender), out)
        return out
