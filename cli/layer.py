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

from .queue import QueueItem
from . import myemoji
import os
import binascii
import logging
logger = logging.getLogger(__name__)


class WebsupLayer(YowInterfaceLayer):
    EVENT_START = "org.openwhatsapp.yowsup.event.cli.start"

    def __init__(self):
        YowInterfaceLayer.__init__(self)
        self.queue = None

    def onEvent(self, layerEvent):
        logger.info("Event %s", layerEvent.getName())
        if layerEvent.getName() == self.__class__.EVENT_START:
            self.queue = layerEvent.getArg('queue')
            logger.info("Started.")
            return True

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
            sender = messageProtocolEntity.getFrom(full=False)
            notify = myemoji.escape(messageProtocolEntity.getNotify())
            if notify and notify != sender:
                sender = "%s - %s" % (sender, notify)
            text = myemoji.replace(text)
            sender = myemoji.replace(sender)
            item = QueueItem(
                timestamp=timestamp, text=text, sender=sender, url=url,
                thumb=thumb, data=messageProtocolEntity,
            )
            self.queue.put(item)
#           logger.debug(item)

    @ProtocolEntityCallback("receipt")
    def onReceipt(self, entity):
        ack = OutgoingAckProtocolEntity(entity.getId(), "receipt", "delivery")
        self.toLower(ack)
