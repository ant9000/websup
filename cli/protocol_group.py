from yowsup.layers.protocol_groups import YowGroupsProtocolLayer
from yowsup.layers.protocol_groups.protocolentities.\
    notification_groups_create \
    import CreateGroupsNotificationProtocolEntity
import logging
logger = logging.getLogger(__name__)


class GroupProtocolLayer(YowGroupsProtocolLayer):
    def recvNotification(self, node):
        if node["type"] == "w:gp2":
            if node.getChild("create"):
                self.toUpper(
                    CreateGroupsNotificationProtocolEntity.
                    fromProtocolTreeNode(node)
                )
            elif node.getChild("add"):
                participant = node.getChild("add").getChild(
                    "participant"
                ).getAttributeValue("jid")
                logger.info(
                    "Group %s: added participant %s" % (
                        node["from"],
                        participant,
                    )
                )
            elif node.getChild("remove"):
                participant = node.getChild("remove").getChild(
                    "participant"
                ).getAttributeValue("jid")
                logger.info(
                    "Group %s: removed participant %s" % (
                        node["from"],
                        participant,
                    )
                )
            else:
                YowGroupsProtocolLayer.recvNotification(self, node)
