from yowsup.stacks import YowStack, YowStackBuilder
from yowsup.layers.network import YowNetworkLayer
from yowsup.layers.auth import AuthError
from yowsup.layers import YowLayerEvent
from yowsup import env
from yowsup.env import S40YowsupEnv
import sys
import gevent
from .layer import WebsupLayer


# patch to support audio / video messages
from yowsup.layers.protocol_media import YowMediaProtocolLayer
from yowsup.layers.protocol_media.protocolentities \
    import DownloadableMediaMessageProtocolEntity as DownloadableMediaEntity
from yowsup.layers.protocol_media.protocolentities \
    import ImageDownloadableMediaMessageProtocolEntity as ImageMediaEntity


class MyYowMediaProtocolLayer(YowMediaProtocolLayer):
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

class MyStackBuilder(YowStackBuilder):
    def build(self):
        layers = []
        for layer in self.layers:
            if layer == YowMediaProtocolLayer:
                layer = MyYowMediaProtocolLayer
            layers.append(layer)
        return YowStack(layers, reversed=False)
# end patch


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
                self.stack.loop(timeout=0.5, count=1)
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
