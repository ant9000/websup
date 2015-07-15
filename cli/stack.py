from yowsup.stacks import YowStackBuilder
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
    def __init__(self, credentials, name, encryptionEnabled=False):
        stackBuilder = YowStackBuilder()
        if not encryptionEnabled:
            env.CURRENT_ENV = S40YowsupEnv()
        self.stack = stackBuilder\
            .pushDefaultLayers(encryptionEnabled)\
            .push(WebsupLayer)\
            .build()
        self.stack.setCredentials(credentials)
        self.stack.setProp('name', name)
        self.stack.setProp('loop', True)

    def start(self, queue):
        try:
            self.stack.broadcastEvent(
                YowLayerEvent(WebsupLayer.EVENT_START, queue=queue)
            )
            while self.stack.getProp('loop'):
                try:
                    self.stack.loop(timeout=0.5, count=1)
                except ValueError, e:
                    logger.error("%s", e)
                gevent.sleep(0.5)
            logger.warning('stopped.')
        except AuthError as e:
            print("Auth Error, reason %s" % e)
        except KeyboardInterrupt, e:
            print("Exit.")
            sys.exit(0)
        except Exception as e:
            print("Caught exception: %s" % e)

    def dispatch(self, item):
        self.stack.broadcastEvent(
            YowLayerEvent(WebsupLayer.EVENT_DISPATCH, item=item)
        )
