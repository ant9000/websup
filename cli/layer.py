from yowsup.layers.interface import YowInterfaceLayer, ProtocolEntityCallback
from yowsup.layers.protocol_messages.protocolentities import \
    TextMessageProtocolEntity
from yowsup.layers.protocol_media.protocolentities import \
    ImageDownloadableMediaMessageProtocolEntity, \
    LocationMediaMessageProtocolEntity, \
    VCardMediaMessageProtocolEntity
from yowsup.layers.protocol_receipts.protocolentities import \
    OutgoingReceiptProtocolEntity
from yowsup.layers.protocol_acks.protocolentities import \
    OutgoingAckProtocolEntity
from yowsup.layers.network import YowNetworkLayer
from yowsup.layers.protocol_groups.protocolentities import \
    ListGroupsIqProtocolEntity, \
    ListGroupsResultIqProtocolEntity, \
    ParticipantsGroupsIqProtocolEntity, \
    ListParticipantsResultIqProtocolEntity, \
    SubjectGroupsNotificationProtocolEntity
from yowsup.layers.protocol_groups.structs.group import Group
from yowsup.layers.protocol_notifications.protocolentities.notification_status \
    import StatusNotificationProtocolEntity
from yowsup.layers.protocol_contacts.protocolentities.notification_contact_update \
    import UpdateContactNotificationProtocolEntity
from yowsup.layers.protocol_notifications.protocolentities.notification_picture \
    import PictureNotificationProtocolEntity

from .queue import QueueItem
from . import myemoji
import os
import binascii
import logging
logger = logging.getLogger(__name__)


class WebsupLayer(YowInterfaceLayer):
    EVENT_START = "org.openwhatsapp.yowsup.event.cli.start"
    EVENT_DISPATCH = "org.openwhatsapp.yowsup.event.cli.dispatch"

    def __init__(self):
        YowInterfaceLayer.__init__(self)
        self.queue = None

    def normalizeJid(self, number):
        if '@' in number:
            return number
        elif "-" in number:
            return "%s@g.us" % number

    def onEvent(self, layerEvent):
        name = layerEvent.getName()
        logger.info("Event %s", name)
        if name == self.__class__.EVENT_START:
            self.queue = layerEvent.getArg('queue')
            logger.info("Started.")
            return True
        elif name == self.__class__.EVENT_DISPATCH:
            item = layerEvent.getArg('item')
            if item.item_type == 'message':
                number = item.content['to']
                content = item.content['content']
                self.message_send(number, content)
            elif item.item_type == 'group':
                data = item.content
                if data['command'] == 'groups-list':
                    self.groups_list()
                elif data['command'] == 'group-participants':
                    if data.get('group_id',None):
                        self.group_participants(data['group_id'])
                # group-create
                # group-subject
                # group-participant-add
                # group-participant-del
                # group-destroy
            return True
        elif name == YowNetworkLayer.EVENT_STATE_CONNECTED:
            logger.info("Connected")
        elif name == YowNetworkLayer.EVENT_STATE_DISCONNECTED:
            logger.warning("Disconnected: %s", layerEvent.getArg('reason'))

    @ProtocolEntityCallback("message")
    def onMessage(self, entity):
        logger.info(
            "Message %s: %s %s - type %s",
            entity.getId(),
            entity.getFrom(),
            entity.getNotify(),
            entity.getType()
        )
        receipt = OutgoingReceiptProtocolEntity(
            entity.getId(),
            entity.getFrom(),
        )
        # send receipt otherwise we keep receiving the same message
        # over and over
        self.toLower(receipt)

        text = ''
        url = ''
        thumb = ''
        if entity.getType() == 'text':
            text = myemoji.escape(entity.getBody() or '')
        elif entity.getType() == 'media':
            url = entity.url
            thumb = entity.getPreview() or ''
            media_type = entity.getMediaType()
            if media_type in ["image", "video"]:
                text = myemoji.escape(entity.getCaption() or '')
            elif media_type == "audio":
                text = ''  # audio has no caption
            elif media_type == "location":
                text = myemoji.escape(
                    entity.getLocationName() or ''
                )
                if not text:
                    text = "Location: (%s,%s)" % (
                        entity.getLatitude(),
                        entity.getLongitude(),
                    )
                if not url:
                    url = 'http://www.osm.org/#map=16/%s/%s' % (
                        entity.getLatitude(),
                        entity.getLongitude(),
                    )
            if thumb:
                # encode as data-uri
                thumb = 'data:%s;base64,%s' % (
                    'image/jpeg',
                    binascii.b2a_base64(thumb).strip(),
                )
            if not (text or thumb):
                text = '%s message [%s]' % (
                    media_type,
                    entity.getMimeType(),
                )

        if text or url:
            notify = myemoji.escape(entity.getNotify())
            notify = myemoji.replace(notify)
            text = myemoji.replace(text)
            item = QueueItem(
                item_type='message',
                content={
                   'id': entity.getId(),
                   'timestamp': entity.getTimestamp(),
                   'from': entity.getFrom(full=True),
                   'to': entity.getTo(full=True),
                   'content': text,
                   'url': url,
                   'thumb': thumb,
                   'notify': notify,
                   'is_group': entity.isGroupMessage(),
                   'participant': entity.getParticipant(full=True) or '',
                }
            )
            self.queue.put(item)
#           logger.debug(item)

    @ProtocolEntityCallback("receipt")
    def onReceipt(self, entity):
        ack = OutgoingAckProtocolEntity(entity.getId(), "receipt", "delivery")
        self.toLower(ack)

    def message_send(self, number, content):
        logger.info('Sending message to %s: %s' % (number, content))
        outgoingMessage = TextMessageProtocolEntity(
            content.encode('utf-8'), to=self.normalizeJid(number)
        )
        self.toLower(outgoingMessage)

    def groups_list(self):
        entity = ListGroupsIqProtocolEntity()
        logger.info('Asking for group list.')
        self.toLower(entity)

    def group_participants(self, group_jid):
        entity = ParticipantsGroupsIqProtocolEntity(self.normalizeJid(group_jid))
        logger.info('Group %s, asking for participants.' % group_jid)
        self.toLower(entity)

    @ProtocolEntityCallback("success")
    def onSuccess(self, entity):
        self.connected = True
        logger.info("Logged in!")

    @ProtocolEntityCallback("failure")
    def onFailure(self, entity):
        self.connected = False
        logger.warning("Login Failed, reason: %s" % entity.getReason())

    @ProtocolEntityCallback("iq")
    def onIq(self, entity):
        if isinstance(entity, ListGroupsResultIqProtocolEntity):
            logger.info('Group list results:')
            if entity.getGroups():
                for group in entity.getGroups():
                    logger.info('- %s' % group)
                    item = QueueItem(
                        item_type='group',
                        content={
                            'id': self.normalizeJid(group.getId()),
                            'owner': group.getOwner(),
                            'created': group.getCreationTime(),
                            'subject': group.getSubject(),
                            'subject-owner': group.getSubjectOwner(),
                            'subject-time': group.getSubjectTime(),
                        }
                    )
                    self.queue.put(item)
                    self.group_participants(group.getId())
            else:
                logger.info('- no groups')
        elif isinstance(entity, ListParticipantsResultIqProtocolEntity):
            logger.info('Group %s participants:' % entity.getFrom())
            if entity.getParticipants():
                item = QueueItem(
                    item_type='group',
                    content={
                        'id': entity.getFrom(),
                        'participants': entity.getParticipants(),
                    }
                )
                self.queue.put(item)
                for participant in entity.getParticipants():
                    logger.info('- %s' % participant)
            else:
                logger.info('- no participants')
        else:
            logger.info('Iq received entity %s' % entity.__class__)

    @ProtocolEntityCallback("notification")
    def onNotification(self, entity):
        if isinstance(entity, SubjectGroupsNotificationProtocolEntity):
            logger.info(
                'Group %s new subject: "%s"' % (
                    entity.getFrom(), entity.getSubject()
                )
            )
            item = QueueItem(
                item_type='group',
                content={
                    'id': group.getFrom(),
                    'subject': group.getSubject(),
                    'subject-owner': group.getSubjectOwner(),
                    'subject-time': group.getSubjectTime(),
                }
            )
            self.queue.put(item)
        elif isinstance(entity, StatusNotificationProtocolEntity):
            logger.info(
                'Status %s for "%s" %s' % (
                    entity.status,
                    entity.notify,
                    entity.getFrom()
                )
            )
#       elif isinstance(entity, UpdateContactNotificationProtocolEntity):
#       elif isinstance(entity, PictureNotificationProtocolEntity):
        else:
            logger.info('Notification received entity %s' % entity.__class__)

    @ProtocolEntityCallback("presence")
    def onPresence(self, entity):
        logger.info('Presence received entity %s' % entity)
