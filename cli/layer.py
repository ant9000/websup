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
    CreateGroupsIqProtocolEntity, \
    SuccessCreateGroupsIqProtocolEntity, \
    SubjectGroupsIqProtocolEntity, \
    SubjectGroupsNotificationProtocolEntity, \
    DeleteGroupsIqProtocolEntity, \
    AddParticipantsIqProtocolEntity
from yowsup.layers.protocol_groups.protocolentities.notification_groups_create import \
    CreateGroupsNotificationProtocolEntity
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
from operator import itemgetter
import logging
logger = logging.getLogger(__name__)


class WebsupLayer(YowInterfaceLayer):
    EVENT_START = "org.openwhatsapp.yowsup.event.cli.start"
    EVENT_DISPATCH = "org.openwhatsapp.yowsup.event.cli.dispatch"

    def __init__(self):
        YowInterfaceLayer.__init__(self)
        self.queue = None
        self.pending_iqs = {}

    def normalizeJid(self, number):
        if "@" in number:
            return number
        elif "-" in number:
            return "%s@g.us" % number
        return "%s@s.whatsapp.net" % number

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
                    if data.get('group_id', None):
                        self.group_participants(data['group_id'])
                elif data['command'] == 'create':
                    if data.get('subject', None):
                        self.group_create(data['subject'])
                elif data['command'] == 'subject':
                    if data.get('group_id', None) and \
                            data.get('subject', None):
                        self.group_subject(data['group_id'], data['subject'])
                elif data['command'] == 'delete':
                    if data.get('group_id', None):
                        self.group_delete(data['group_id'])
                elif data['command'] == 'participants':
                    if data.get('group_id', None):
                        participants = {}
                        for l in ['old', 'new']:
                            participants[l] = set([
                                self.normalizeJid(p.strip())
                                for p in data.get(l, [])
                                if p.strip()
                            ])
                        to_add = participants['new'] - participants['old']
                        to_del = participants['old'] - participants['new']
                        logger.info(
                            'Edit group %s participants: old=%s, new=%s' % (
                                data['group_id'],
                                participants['old'],
                                participants['new'],
                            )
                        )
                        logger.info('Participants to add: %s' % to_add)
                        logger.info('Participants to remove: %s' % to_del)
                        for participant in to_add:
                            self.group_participant_add(data['group_id'], participant)
                        for participant in to_del:
                            self.group_participant_del(data['group_id'], participant)
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

    @ProtocolEntityCallback("ack")
    def onAck(self, entity):
        if entity.getClass() == "message":
            # TODO: Sent
            pass

    def message_send(self, number, content):
        logger.info('Sending message to %s: %s' % (number, content))
        outgoingMessage = TextMessageProtocolEntity(
            content.encode('utf-8'), to=self.normalizeJid(number)
        )
        self.toLower(outgoingMessage)

    def groups_list(self):
        entity = ListGroupsIqProtocolEntity()
        logger.info('Asking for groups list.')
        self.toLower(entity)

    def group_participants(self, group_id):
        entity = ParticipantsGroupsIqProtocolEntity(
            self.normalizeJid(group_id)
        )
        logger.info('Group %s, asking for participants.' % group_id)
        self.toLower(entity)

    def group_create(self, subject):
        entity = CreateGroupsIqProtocolEntity(subject)
        logger.info('Creating new group with subject "%s"' % subject)
        self.pending_iqs[entity.getId()] = {
            'group_id': None,
            'subject': subject
        }
        self.toLower(entity)

    def group_delete(self, group_id):
        # TODO: does not work
        entity = DeleteGroupsIqProtocolEntity(self.normalizeJid(group_id))
        logger.info('Deleting group %s.' % group_id)
        self.toLower(entity)

    def group_subject(self, group_id, subject):
        entity = SubjectGroupsIqProtocolEntity(
            self.normalizeJid(group_id), subject
        )
        logger.info('Change subject of group %s to "%s"' % (group_id, subject))
        self.toLower(entity)

    def group_participant_add(self, group_id, participant):
        entity = AddParticipantsIqProtocolEntity(
            self.normalizeJid(group_id),
            self.normalizeJid(participant),
        )
        self.pending_iqs[entity.getId()] = {
            'group_id': group_id,
            'participant': participant,
        }
        logger.info('Group %s, add participant %s' % (group_id, participant))
        logger.info(entity.toProtocolTreeNode())
        self.toLower(entity)

    def group_participant_del(self, group_id, participant):
        # TODO
        logger.info('Group %s, del participant %s' % (group_id, participant))

    @ProtocolEntityCallback("success")
    def onSuccess(self, entity):
        self.connected = True
        item = QueueItem(
            item_type='session',
            content={
                'status': 'logged in',
            },
        )
        self.queue.put(item)
        logger.info("Logged in!")

    @ProtocolEntityCallback("failure")
    def onFailure(self, entity):
        self.connected = False
        item = QueueItem(
            item_type='session',
            content={
                'status': 'error',
                'message': entity.getReason(),
            }
        )
        self.queue.put(item)
        logger.error("Login Failed, reason: %s" % entity.getReason())

    @ProtocolEntityCallback("iq")
    def onIq(self, entity):
        if isinstance(entity, ListGroupsResultIqProtocolEntity):
            msg = ['Group list results:']
            if entity.getGroups():
                groups = []
                for group in entity.getGroups():
                    msg.append('- %s' % group)
                    groups.append({
                        'id': self.normalizeJid(group.getId()),
                        'owner': group.getOwner(),
                        'created': group.getCreationTime(),
                        'subject': group.getSubject(),
                        'subject-owner': group.getSubjectOwner(),
                        'subject-time': group.getSubjectTime(),
                    })
                    self.group_participants(group.getId())
                item = QueueItem(
                    item_type='group-list',
                    content={ 'groups': sorted(groups,key=itemgetter('subject')), }
                )
                self.queue.put(item)
            else:
                msg.append('- no groups')
            logger.info('\n'.join(msg))
        elif isinstance(entity, ListParticipantsResultIqProtocolEntity):
            msg = [ 'Group %s participants:' % entity.getFrom() ]
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
                    msg.append('- %s' % participant)
            else:
                msg.append('- no participants')
            logger.info('\n'.join(msg))
#       elif isinstance(entity, SuccessCreateGroupsIqProtocolEntity):
#           group = self.pending_iqs.get(entity.getId(), None)
#           if group:
#               del self.pending_iqs[entity.getId()]
#               logger.info(
#                   'Group "%s" created with id %s' % (
#                       group['subject'], entity.groupId
#                   )
#               )
#               item = QueueItem(
#                   item_type='group',
#                   content={
#                       'id': self.normalizeJid(entity.groupId),
#                       'subject': group['subject'],
#                   }
#               )
#               self.queue.put(item)
        else:
            logger.info('Iq received entity:\n%s' % entity.toProtocolTreeNode())

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
                    'id': entity.getFrom(),
                    'subject': entity.getSubject(),
                    'subject-owner': entity.getSubjectOwner(),
                    'subject-time': entity.getSubjectTimestamp(),
                }
            )
            self.queue.put(item)
        elif isinstance(entity, CreateGroupsNotificationProtocolEntity):
            logger.info(
                'New group %s with subject: "%s"' % (
                    entity.getGroupId(), entity.getSubject()
                )
            )
            item = QueueItem(
                item_type='group',
                content={
                    'id': self.normalizeJid(entity.getGroupId()),
                    'owner': entity.getCreatorJid(),
                    'created': entity.getCreationTimestamp(),
                    'subject': entity.getSubject(),
                    'subject-owner': entity.getSubjectOwnerJid(),
                    'subject-time': entity.getSubjectTimestamp(),
                    'participants': entity.getParticipants(),
                }
            )
            self.queue.put(item)
        else:
            logger.info('Notification received entity:\n%s' % entity.toProtocolTreeNode())

    @ProtocolEntityCallback("presence")
    def onPresence(self, entity):
        logger.info('Presence received entity %s' % entity)
