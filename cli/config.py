from ConfigParser import RawConfigParser, NoSectionError, NoOptionError
import os


class Config(RawConfigParser):

    DEFAULT_CFG = """[whatsapp]
phone =
password =

[webpage]
username = admin
password = admin

[email]
from =
to =
; recognized format:
; (smtp|starttls|ssl)://[username:password@]<hostname or ip>[:port]
server =
"""

    def __init__(self, filename):
        RawConfigParser.__init__(self)
        self.filename = filename
        if not os.path.isfile(self.filename):
            open(self.filename, 'w').write(self.DEFAULT_CFG)
        self.read(self.filename)

    def save(self):
        f = open(self.filename, 'w')
        self.write(f)
        f.close()
