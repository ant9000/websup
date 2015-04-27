from yowsup.stacks import YowStackBuilder
from yowsup.layers.network import YowNetworkLayer
from yowsup.layers.auth import AuthError
from yowsup.layers import YowLayerEvent
from yowsup import env
from yowsup.env import S40YowsupEnv
import sys
import gevent
from .layer import WebsupLayer
import logging
logger = logging.getLogger(__name__)


class WebsupStack(object):
    def __init__(self, credentials, encryptionEnabled=False):
        stackBuilder = YowStackBuilder()
        if not encryptionEnabled:
            env.CURRENT_ENV = S40YowsupEnv()
        self.stack = stackBuilder\
            .pushDefaultLayers(encryptionEnabled)\
            .push(WebsupLayer)\
            .build()
        self.stack.setCredentials(credentials)

    def start(self, queue):
        self.stack.broadcastEvent(
            YowLayerEvent(WebsupLayer.EVENT_START, queue=queue)
        )
        self.stack.broadcastEvent(
            YowLayerEvent(YowNetworkLayer.EVENT_STATE_CONNECT)
        )
        try:
            while True:
                try:
                    self.stack.loop(timeout=0.5, count=1)
                except ValueError, e:
                    logger.error("%s", e)
                gevent.sleep(0.5)
        except AuthError as e:
            print("Auth Error, reason %s" % e)
        except KeyboardInterrupt, e:
            print "Exit."
            sys.exit(0)

    def dispatch(self, item):
        self.stack.broadcastEvent(
            YowLayerEvent(WebsupLayer.EVENT_DISPATCH, item=item)
        )
