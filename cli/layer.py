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
        logger.info("Event %s" % layerEvent.getName())
        if layerEvent.getName() == self.__class__.EVENT_START:
            self.queue = layerEvent.getArg('queue')
            logger.info("Started.")
            return True

    @ProtocolEntityCallback("message")
    def onMessage(self, messageProtocolEntity):
        receipt = OutgoingReceiptProtocolEntity(
            messageProtocolEntity.getId(),
            messageProtocolEntity.getFrom(),
        )
        # send receipt otherwise we keep receiving the same message
        # over and over
        self.toLower(receipt)

        text = None
        if messageProtocolEntity.getType() == 'text':
            text = myemoji.escape(messageProtocolEntity.getBody())
        elif messageProtocolEntity.getType() == 'media':
            media_type = messageProtocolEntity.getMediaType()
            if media_type in ["image", "audio", "video"]:
                text = myemoji.escape(messageProtocolEntity.getCaption())
                thumb = messageProtocolEntity.getPreview()
                if media_type == "image" and thumb:
                    # encode as data-uri
                    text = '<img src="data:%s;base64,%s" title="%s"/>' % (
                        'image/jpeg',
                        binascii.b2a_base64(thumb),
                        myemoji.escapejs(messageProtocolEntity.getCaption())
                    )
                text = '%s: <a href="%s" target="_new">%s</a>' % (
                    media_type.capitalize(),
                    messageProtocolEntity.url,
                    text,
                )
            elif media_type == "location":
                text = "Location: (%s,%s)" % (
                    messageProtocolEntity.getLatitude(),
                    messageProtocolEntity.getLongitude(),
                )
        if text:
            sender = messageProtocolEntity.getFrom(full=False)
            notify = myemoji.escape(messageProtocolEntity.getNotify())
            if notify:
                sender = "%s - %s" % (sender, notify)
            text = myemoji.replace(text)
            sender = myemoji.replace(sender)
            item = QueueItem(text, sender, messageProtocolEntity)
            self.queue.put(item)
            logger.debug(item)

    @ProtocolEntityCallback("receipt")
    def onReceipt(self, entity):
        ack = OutgoingAckProtocolEntity(entity.getId(), "receipt", "delivery")
        self.toLower(ack)
