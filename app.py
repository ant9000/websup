#!/usr/bin/env python

import logging
import logging.config
logging.config.fileConfig('logging.conf')

import sys
import gevent
import bottle
from bottle.ext.websocket import GeventWebSocketServer
from bottle.ext.websocket import websocket
from geventwebsocket import WebSocketError
from cli.config import Config, NoSectionError, NoOptionError
from cli import stack
from cli.queue import Queue, QueueItem
from cli import myemoji
import os


def here(path):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), path))

try:
    cfg = Config(here('configuration.ini'))
    phone = cfg.get('whatsapp', 'phone')
    password = cfg.get('whatsapp', 'password')
    if not phone:
        raise NoOptionError('phone', 'whatsapp')
    if not password:
        raise NoOptionError('password', 'whatsapp')
except:
    print """
ERROR: check file "configuration.ini" and make sure the Whatsapp
credentials are correct.

Use the command

  yowsup-cli registration help

for getting further help.
  """
    sys.exit(1)

logger = logging.getLogger()
queue = Queue()
stack = stack.WebsupStack((phone, password))
users = set()

@bottle.route('/')
def index():
    return bottle.static_file('index.html', root=here('static'))


@bottle.route('/websocket', apply=[websocket])
def echo(ws):
    users.add(ws)
    while True:
        try:
            msg = ws.receive()
            if msg is not None:
                logger.info(msg)
            for item in queue:
                for user in users:
                    msg = item.toJson()
                    user.send(msg)
        except WebSocketError, e:
            logger.error(e)
            break


@bottle.route('/static/emoji/<filename:path>')
def send_static(filename):
    return bottle.static_file(filename, root=myemoji.EMOJI_STATIC_ROOT)


@bottle.route('/static/<filename:path>')
def send_static(filename):
    return bottle.static_file(filename, root=here('static'))


def yowsup():
    stack.start(queue)


try:
    gevent.spawn(yowsup)
    bottle.run(host='127.0.0.1', port=8080, server=GeventWebSocketServer)
except KeyboardInterrupt:
    print "Exit."
