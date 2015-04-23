from yowsup.layers.protocol_groups import YowGroupsProtocolLayer
from yowsup.layers.protocol_groups.protocolentities.\
    notification_groups_create \
    import CreateGroupsNotificationProtocolEntity
from yowsup.layers.protocol_groups.protocolentities \
    import LeaveGroupsIqProtocolEntity
from .entities import SuccessLeaveGroupsIqProtocolEntity 
import logging
logger = logging.getLogger(__name__)


class GroupProtocolLayer(YowGroupsProtocolLayer):
    def sendIq(self, entity):
        if entity.__class__ == LeaveGroupsIqProtocolEntity:
            self._sendIq(entity, self.onLeaveGroupSuccess, self.onLeaveGroupFailed)
        else:
            YowGroupsProtocolLayer.sendIq(self, entity)

    def onLeaveGroupSuccess(self, node, originalIqEntity):
        logger.info("Group leave success")
        self.toUpper(SuccessLeaveGroupsIqProtocolEntity.fromProtocolTreeNode(node))

    def onLeaveGroupFailed(self, node, originalIqEntity):
        logger.error("Group leave failed")

    def recvNotification(self, node):
        if node["type"] == "w:gp2":
            if node.getChild("create"):
                self.toUpper(
                    CreateGroupsNotificationProtocolEntity.
                    fromProtocolTreeNode(node)
                )
            else:
                YowGroupsProtocolLayer.recvNotification(self, node)
