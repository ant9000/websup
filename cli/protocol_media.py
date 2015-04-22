from yowsup.layers.protocol_media import YowMediaProtocolLayer
from yowsup.layers.protocol_media.protocolentities \
    import DownloadableMediaMessageProtocolEntity as DownloadableMediaEntity
from yowsup.layers.protocol_media.protocolentities \
    import ImageDownloadableMediaMessageProtocolEntity as ImageMediaEntity

class MediaProtocolLayer(YowMediaProtocolLayer):
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
