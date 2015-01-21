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

import os
import logging
logger = logging.getLogger(__name__)


class WebsupLayer(YowInterfaceLayer):
    EVENT_START = "org.openwhatsapp.yowsup.event.cli.start"

    def __init__(self):
        YowInterfaceLayer.__init__(self)
        self.queue = None

    def output(self, text, sender=None, data=None):
        out = {
            'text':   text,
            'sender': sender,
            'data':   data,
        }
        if self.queue:
            self.queue.put(out)
        print(out)

    def onEvent(self, layerEvent):
        self.output("Event %s" % layerEvent.getName())
        if layerEvent.getName() == self.__class__.EVENT_START:
            self.queue = layerEvent.getArg('queue')
            self.output("Started.")
            return True

    @ProtocolEntityCallback("message")
    def onMessage(self, messageProtocolEntity):
        if not messageProtocolEntity.isGroupMessage():
            text, outMessage = None, None
            receipt = OutgoingReceiptProtocolEntity(
                messageProtocolEntity.getId(), messageProtocolEntity.getFrom()
            )
            if messageProtocolEntity.getType() == 'text':
                text = messageProtocolEntity.getBody()
                outMessage = TextMessageProtocolEntity(
                    messageProtocolEntity.getBody(),
                    to=messageProtocolEntity.getFrom(),
                )
            elif messageProtocolEntity.getType() == 'media':
                if messageProtocolEntity.getMediaType() == "image":
                    text = messageProtocolEntity.url
                    outMessage = ImageDownloadableMediaMessageProtocolEntity(
                        messageProtocolEntity.getMimeType(),
                        messageProtocolEntity.fileHash,
                        messageProtocolEntity.url,
                        messageProtocolEntity.ip,
                        messageProtocolEntity.size,
                        messageProtocolEntity.fileName,
                        messageProtocolEntity.encoding,
                        messageProtocolEntity.width,
                        messageProtocolEntity.height,
                        messageProtocolEntity.getCaption(),
                        to=messageProtocolEntity.getFrom(),
                        preview=s messageProtocolEntity.getPreview(),
                    )
                elif messageProtocolEntity.getMediaType() == "location":
                    text = "(%s,%s)" % (
                        messageProtocolEntity.getLatitude(),
                        messageProtocolEntity.getLongitude(),
                    )
                    outMessage = LocationMediaMessageProtocolEntity(
                        messageProtocolEntity.getLatitude(),
                        messageProtocolEntity.getLongitude(),
                        messageProtocolEntity.getLocationName(),
                        messageProtocolEntity.getLocationURL(),
                        messageProtocolEntity.encoding,
                        to=messageProtocolEntity.getFrom(),
                        preview=messageProtocolEntity.getPreview(),
                    )
                elif messageProtocolEntity.getMediaType() == "vcard":
                    text = "%s:%s" % (
                        messageProtocolEntity.getName(),
                        messageProtocolEntity.getCardData(),
                    )
                    outMessage = VCardMediaMessageProtocolEntity(
                        messageProtocolEntity.getName(),
                        messageProtocolEntity.getCardData(),
                        to=messageProtocolEntity.getFrom(),
                    )
            if outMessage:
                # send receipt otherwise we keep receiving the same message
                # over and over
                self.toLower(receipt)
                self.toLower(outMessage)
                self.output(
                    text, messageProtocolEntity.getFrom(full=False), outMessage
                )

    @ProtocolEntityCallback("receipt")
    def onReceipt(self, entity):
        ack = OutgoingAckProtocolEntity(entity.getId(), "receipt", "delivery")
        self.toLower(ack)
