from yowsup.stacks import YowStack, YOWSUP_CORE_LAYERS, YOWSUP_PROTOCOL_LAYERS_FULL
from yowsup.layers.axolotl import YowAxolotlLayer
from .layer import WebsupLayer
from yowsup.common import YowConstants
from yowsup.layers.network import YowNetworkLayer
from yowsup.layers.auth import AuthError
from yowsup.layers.coder import YowCoderLayer
from yowsup.layers import YowLayerEvent
from yowsup.layers.auth import YowAuthenticationProtocolLayer
from yowsup import env
from yowsup.env import S40YowsupEnv
import sys
import gevent

class WebsupStack(object):
    def __init__(self, credentials, encryptionEnabled = False):
        env.CURRENT_ENV = env.S40YowsupEnv()
        layers = [WebsupLayer, YOWSUP_PROTOCOL_LAYERS_FULL ]
        if encryptionEnabled:
            layers += [YowAxolotlLayer]
        layers += YOWSUP_CORE_LAYERS
        self.stack = YowStack(layers)
        self.stack.setProp(YowAuthenticationProtocolLayer.PROP_CREDENTIALS, credentials)
        self.stack.setProp(YowNetworkLayer.PROP_ENDPOINT, YowConstants.ENDPOINTS[0])
        self.stack.setProp(YowCoderLayer.PROP_DOMAIN, YowConstants.DOMAIN)
        self.stack.setProp(YowCoderLayer.PROP_RESOURCE, env.CURRENT_ENV.getResource())

    def start(self,queue):
        self.stack.broadcastEvent(YowLayerEvent(WebsupLayer.EVENT_START,queue=queue))
        self.stack.broadcastEvent(YowLayerEvent(YowNetworkLayer.EVENT_STATE_CONNECT))
        try:
            while True:
                self.stack.loop(timeout = 0.5, count = 1)
                gevent.sleep(0.5)
        except AuthError as e:
            print("Auth Error, reason %s" % e)
        except KeyboardInterrupt, e:
            print "Exit."
            sys.exit(0)
