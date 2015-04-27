from cork.cork import Mailer as CorkMailer, AAAException
from base64 import b64encode, b64decode
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.encoders import encode_noop
from threading import Thread
import logging
import re

logger = logging.getLogger(__name__)


def extract_datauris(text):
    r1 = re.compile('src="data:(?P<mimetype>[^;]+);base64,(?P<content>[^"]+)"')
    r2 = re.compile('src="(data:[^"]+)"')
    body = text
    images = []
    i = 1
    while True:
        m = r1.search(body)
        if not m:
            break
        img = m.groupdict()
        img['content_id'] = 'image_%d' % i
        img['content'] = b64decode(img['content'])
        body = r2.sub('src="cid:%(content_id)s"' % img, body, count=1)
        images.append(img)
        i += 1
    return (body, images)


def compose_email(sender, email_addr, subject, email_text):
    msg = MIMEMultipart('related')
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = email_addr
    body, images = extract_datauris(email_text)
    part = MIMEText(body, 'html')
    msg.attach(part)
    for img in images:
        part = MIMEImage(img['content'], img['mimetype'])
        part.add_header('Content-ID', '<{}>'.format(img['content_id']))
        msg.attach(part)
    return msg


class Mailer(CorkMailer):
    def send_email(self, email_addr, subject, email_text):
        """Send an email - substituting datauris with attachments

        :param email_addr: email address
        :type email_addr: str.
        :param subject: subject
        :type subject: str.
        :param email_text: email text
        :type email_text: str.
        :raises: AAAException if smtp_server and/or sender are not set
        """
        if not (self._conf['fqdn'] and self.sender):
            raise AAAException("SMTP server or sender not set")
        msg = compose_email(self.sender, email_addr, subject, email_text)
        logger.debug("Sending email using %s" % self._conf['fqdn'])
        thread = Thread(target=self._send, args=(email_addr, msg.as_string()))
        thread.start()
        self._threads.append(thread)


if __name__ == "__main__":
    test_html = """
<!doctype html>
<head>
<style>
body {
  font:1em/1.4 Cambria, Georgia, sans-serif;
  color:#333;
  background:#fff;
}
.emoji { width: 18px; height: 18px; }
p { font-size: 70%; padding: 0; margin: 0; }
.number { font-weight: bold; }
</style>
</head>
<body>
<p>
  [<span class="time">2015-01-29 15:32:06</span>]
  <span class="number">test</span>
</p>
<hr />
<a href="https://mmi201.whatsapp.net/d/XT0Rm30EhbOFXMLgKy8tv1TKRGYABQ3LWjPuag/AspZNIqxyJb-gqG3_-7-sq-nSslfih0o816YwIfhyUg_.jpg" target="_blank"><img src="data:image/jpeg;base64,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"/><span></span></a>
<a href="https://mmi201.whatsapp.net/d/XT0Rm30EhbOFXMLgKy8tv1TKRGYABQ3LWjPuag/AspZNIqxyJb-gqG3_-7-sq-nSslfih0o816YwIfhyUg_.jpg" target="_blank"><img src="data:image/jpeg;base64,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"/><span></span></a>
</body>
</html>
  """
    body, images = extract_datauris(test_html)
    print body
    for img in images:
        print img['content_id'], img['mimetype']

    print compose_email('from@mail', 'to@mail', 'subject', test_html)
