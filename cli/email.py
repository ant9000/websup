import smtplib
from email.mime.text import MIMEText


class Email:

    def __init__(
        self, host='localhost', port=25, use_ssl=False,
        username=None, password=None, debug=False
    ):
        self.host = host
        self.port = port
        self.use_ssl = use_ssl
        self.username = username
        self.password = password
        self.debug = debug

    def connect(self):
        SMTP = smtplib.SMTP
        if self.use_ssl:
            SMTP = smtplib.SMTP_SSL
        smtp = SMTP(self.host, self.port)
        smtp.set_debuglevel(self.debug)
        if self.username:
            smtp.login(self.username, self.password)
        return smtp

    def send(frm, dst, subj, msg):
        email = MIMEText(msg)
        email['Subject'] = subj
        email['From'] = frm
        email['To'] = dst
        sess = self.connect()
        sess.sendmail(frm, [dst], email.as_string())
        sess.quit()
