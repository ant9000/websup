from yowsup.stacks import YowStack, YowStackBuilder
from yowsup.layers.network import YowNetworkLayer
from yowsup.layers.auth import AuthError
from yowsup.layers import YowLayerEvent, YowParallelLayer
from yowsup import env
from yowsup.env import S40YowsupEnv
import sys
import gevent
from .layer import LoggedInSignalLayer, WebsupLayer
import logging
logger = logging.getLogger(__name__)


# patch to support audio / video messages
from yowsup.layers.protocol_media import YowMediaProtocolLayer
from yowsup.layers.protocol_media.protocolentities \
    import DownloadableMediaMessageProtocolEntity as DownloadableMediaEntity
from yowsup.layers.protocol_media.protocolentities \
    import ImageDownloadableMediaMessageProtocolEntity as ImageMediaEntity


class MyYowMediaProtocolLayer(YowMediaProtocolLayer):
    def __str__(self):
        return "My Media Layer"

    def recvMessageStanza(self, node):
        if node.getAttributeValue("type") == "media":
            mediaNode = node.getChild("media")
            if mediaNode.getAttributeValue("type") == "video":
                entity = ImageMediaEntity.fromProtocolTreeNode(node)
                self.toUpper(entity)
            elif mediaNode.getAttributeValue("type") == "audio":
                entity = DownloadableMediaEntity.fromProtocolTreeNode(node)
                self.toUpper(entity)
            else:
                return YowMediaProtocolLayer.recvMessageStanza(self, node)
# end patch


class MyStackBuilder(YowStackBuilder):
    def build(self):
        def replace(layer,oldtype,newtype):
            if type(layer) == oldtype:
              layer = newtype()
            elif type(layer) == YowParallelLayer:
               layer.sublayers = tuple(
                   [ replace(l,oldtype,newtype) for l in layer.sublayers ]
               )
            return layer

        layers = []
        layers.append(LoggedInSignalLayer)
        for layer in self.layers:
            layers.append(
                replace(layer,YowMediaProtocolLayer,MyYowMediaProtocolLayer)
            )
#       for layer in layers:
#           print layer
#           if type(layer) == YowParallelLayer:
#               for l in layer.sublayers:
#                   print '\t',l 
        return YowStack(layers, reversed=False)


class WebsupStack(object):
    def __init__(self, credentials, encryptionEnabled=False):
        stackBuilder = MyStackBuilder()

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

    def send(self, number, content):
        self.stack.broadcastEvent(
            YowLayerEvent(
                WebsupLayer.EVENT_SEND, number=number, content=content
            )
        )
