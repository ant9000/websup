from yowsup.stacks import YowStack, YOWSUP_CORE_LAYERS, \
    YOWSUP_PROTOCOL_LAYERS_FULL
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
                # TODO: caption support for audio
                entity = DownloadableMediaEntity.fromProtocolTreeNode(node)
                self.toUpper(entity)
            else:
                return YowMediaProtocolLayer.recvMessageStanza(self, node)


YOWSUP_PROTOCOL_LAYERS_FULL_PATCHED = []
for layer in YOWSUP_PROTOCOL_LAYERS_FULL:
    if layer == YowMediaProtocolLayer:
        layer = MyYowMediaProtocolLayer
    YOWSUP_PROTOCOL_LAYERS_FULL_PATCHED.append(layer)
YOWSUP_PROTOCOL_LAYERS_FULL = tuple(YOWSUP_PROTOCOL_LAYERS_FULL_PATCHED)
# end patch


class WebsupStack(object):
    def __init__(self, credentials, encryptionEnabled=False):
        env.CURRENT_ENV = env.S40YowsupEnv()
        layers = [WebsupLayer, YOWSUP_PROTOCOL_LAYERS_FULL]
        if encryptionEnabled:
            layers += [YowAxolotlLayer]
        layers += YOWSUP_CORE_LAYERS
        self.stack = YowStack(layers)
        self.stack.setProp(
            YowAuthenticationProtocolLayer.PROP_CREDENTIALS, credentials
        )
        self.stack.setProp(
            YowNetworkLayer.PROP_ENDPOINT, YowConstants.ENDPOINTS[0]
        )
        self.stack.setProp(
            YowCoderLayer.PROP_DOMAIN, YowConstants.DOMAIN
        )
        self.stack.setProp(
            YowCoderLayer.PROP_RESOURCE, env.CURRENT_ENV.getResource()
        )

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

