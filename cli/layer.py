from yowsup.layers import YowLayer, YowLayerEvent
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
from yowsup.layers.protocol_groups.protocolentities import \
    ListGroupsIqProtocolEntity
from yowsup.layers.network import YowNetworkLayer
from yowsup.layers.auth import YowAuthenticationProtocolLayer

from .queue import QueueItem
from . import myemoji
import os
import binascii
import logging
logger = logging.getLogger(__name__)


# needed to signal successful login to upper layers
class LoggedInSignalLayer(YowLayer):
    EVENT_LOGGED_IN = "org.openwhatsapp.yowsup.event.auth.logged_in"

    def send(self, data):
        self.toLower(data)

    def receive(self, data):
        self.toUpper(data)

    def onEvent(self, yowLayerEvent):
        logger.debug('catched event %s' % yowLayerEvent.getName())
        if yowLayerEvent.getName() == \
                YowAuthenticationProtocolLayer.EVENT_AUTHED:
            self.emitEvent(YowLayerEvent(self.__class__.EVENT_LOGGED_IN))


class WebsupLayer(YowInterfaceLayer):
    EVENT_START = "org.openwhatsapp.yowsup.event.cli.start"
    EVENT_SEND = "org.openwhatsapp.yowsup.event.cli.send"

    def __init__(self):
        YowInterfaceLayer.__init__(self)
        self.queue = None

    def onEvent(self, layerEvent):
        name = layerEvent.getName()
        logger.info("Event %s", name)
        if name == self.__class__.EVENT_START:
            self.queue = layerEvent.getArg('queue')
            logger.info("Started.")
            return True
        elif name == self.__class__.EVENT_SEND:
            number = layerEvent.getArg('number')
            content = layerEvent.getArg('content')
            self.message_send(number, content)
            return True
        elif name == YowNetworkLayer.EVENT_STATE_CONNECTED:
            pass
        elif name == YowNetworkLayer.EVENT_STATE_DISCONNECTED:
            logger.warning("Disconnected: %s", layerEvent.getArg('reason'))
        elif name == LoggedInSignalLayer.EVENT_LOGGED_IN:
            self.groups_list()

    @ProtocolEntityCallback("message")
    def onMessage(self, messageProtocolEntity):
        logger.info(
            "Message %s: %s %s - type %s",
            messageProtocolEntity.getId(),
            messageProtocolEntity.getFrom(),
            messageProtocolEntity.getNotify(),
            messageProtocolEntity.getType()
        )
        receipt = OutgoingReceiptProtocolEntity(
            messageProtocolEntity.getId(),
            messageProtocolEntity.getFrom(),
        )
        # send receipt otherwise we keep receiving the same message
        # over and over
        self.toLower(receipt)

        text = ''
        url = ''
        thumb = ''
        if messageProtocolEntity.getType() == 'text':
            text = myemoji.escape(messageProtocolEntity.getBody() or '')
        elif messageProtocolEntity.getType() == 'media':
            url = messageProtocolEntity.url
            thumb = messageProtocolEntity.getPreview() or ''
            media_type = messageProtocolEntity.getMediaType()
            if media_type in ["image", "video"]:
                text = myemoji.escape(messageProtocolEntity.getCaption() or '')
            elif media_type == "audio":
                text = ''  # audio has no caption
            elif media_type == "location":
                text = myemoji.escape(
                    messageProtocolEntity.getLocationName() or ''
                )
                if not text:
                    text = "Location: (%s,%s)" % (
                        messageProtocolEntity.getLatitude(),
                        messageProtocolEntity.getLongitude(),
                    )
                if not url:
                    url = 'http://www.osm.org/#map=16/%s/%s' % (
                        messageProtocolEntity.getLatitude(),
                        messageProtocolEntity.getLongitude(),
                    )
            if thumb:
                # encode as data-uri
                thumb = '<img src="data:%s;base64,%s"/>' % (
                    'image/jpeg',
                    binascii.b2a_base64(thumb).strip(),
                )
            if not (text or thumb):
                text = '%s message [%s]' % (
                    media_type,
                    messageProtocolEntity.getMimeType(),
                )

        if text or url:
            timestamp = messageProtocolEntity.getTimestamp()
            if messageProtocolEntity.isGroupMessage():
                number = messageProtocolEntity.getParticipant(full=False)
            else:
                number = messageProtocolEntity.getFrom(full=False)
            notify = myemoji.escape(messageProtocolEntity.getNotify())
            if notify == number:
                notify = ''
            text = myemoji.replace(text)
            notify = myemoji.replace(notify)
            item = QueueItem(
                timestamp=timestamp, text=text, number=number, url=url,
                thumb=thumb, notify=notify, data=messageProtocolEntity,
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
            content.encode('utf-8'), to="%s@s.whatsapp.net" % number
        )
        self.toLower(outgoingMessage)

    def groups_list(self):
        entity = ListGroupsIqProtocolEntity()
        logger.info('Asking for group list.')
        self.toLower(entity)
