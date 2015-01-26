from ConfigParser import RawConfigParser, NoSectionError, NoOptionError
import os


class Config(RawConfigParser):

    DEFAULT_CFG = """[whatsapp]
phone =
password =

[webpage]
email =
password =

[smtp]
sender = Whatsapp Forwarder <root@localhost>
server = localhost
port =
use_ssl = False
username =
password =
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
