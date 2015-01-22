#!/usr/bin/env python

import logging
import logging.config
logging.config.fileConfig('logging.conf')

import sys
import json
import gevent
import bottle
from bottle.ext.websocket import GeventWebSocketServer
from bottle.ext.websocket import websocket
from cli import stack
from cli.queue import Queue, QueueItem
from cli import myemoji
import os

try:
    cfg = json.load(open('credentials.json', 'r'))
    phone = cfg['phone']
    password = cfg['password']
except:
    print """
ERROR: file "credentials.json" is missing or invalid.

Check that it exists, it is readable and contains

{
  "phone": "<YOURPHONE>",
  "password": "<YOURPASSWORD>"
}

(substitute YOURPHONE and YOURPASSWORD with the actual
values).

Use the command

  yowsup-cli registration help

for getting further help.
  """
    sys.exit(1)

logger = logging.getLogger()
queue = Queue()
stack = stack.WebsupStack((phone, password))


def here(path):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), path))


@bottle.route('/')
def index():
    return bottle.template('index')


@bottle.route('/websocket', apply=[websocket])
def echo(ws):
    while True:
        try:
            msg = ws.receive()
            if msg is None:
                break
            logger.info(msg)
            for item in queue:
                out = myemoji.replace(unicode(item))
                ws.send(out)
        except WebSocketError:
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
