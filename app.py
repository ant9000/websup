#!/usr/bin/env python

import sys
import json
import gevent
import bottle
from bottle.ext.websocket import GeventWebSocketServer
from bottle.ext.websocket import websocket
from gevent.queue import Queue
from cli import stack
import logging
import logging.config
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

logging.config.fileConfig('logging.conf')
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
        msg = ws.receive()
        if msg is None:
            break
        for item in queue:
            out = item['text']
            if item['sender'] is not None:
                out = '%s: %s' % (item['sender'], item['text'])
            ws.send(out)


@bottle.route('/static/<filename:path>')
def send_static(filename):
    return static_file(filename, root=here('static'))


def yowsup():
    stack.start(queue)

try:
    gevent.spawn(yowsup)
    bottle.run(host='127.0.0.1', port=8080, server=GeventWebSocketServer)
except KeyboardInterrupt:
    print "Exit."
