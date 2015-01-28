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
from beaker.middleware import SessionMiddleware
from cli.config import Config, NoSectionError, NoOptionError
from cli import stack
from cli.queue import Queue, QueueItem
from cli import myemoji
import os
import json


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
session_opts = {
    'session.cookie_expires': True,
    'session.auto': True,
}
app = SessionMiddleware(bottle.app(), session_opts)


def check_login(username, password):
    try:
        if username != '' and \
                username == cfg.get('webpage', 'username') and \
                password == cfg.get('webpage', 'password'):
            return True
    except:
        pass
    return False


@bottle.route('/')
@bottle.view('index')
def index():
    session = bottle.request.environ.get('beaker.session')
    username = session.get('username', None)
    if username is None:
        bottle.redirect('/login')
    return {
        'username': username,
    }


@bottle.route('/login')
@bottle.post('/login')
@bottle.view('login')
def login():
    data = {
        'error': None
    }
    if bottle.request.method == 'POST':
        username = bottle.request.forms.get('username')
        password = bottle.request.forms.get('password')
        if check_login(username, password):
            session = bottle.request.environ.get('beaker.session')
            username = session['username'] = username
            bottle.redirect('/')
        else:
            data['error'] = 'Wrong username or password.'
    return data


@bottle.route('/logout')
def logout():
    session = bottle.request.environ.get('beaker.session')
    session.delete()
    bottle.redirect('/')


users = {}
@bottle.route('/websocket', apply=[websocket])
def echo(ws):
    session = bottle.request.environ.get('beaker.session',{})
    username = session.get('username', None)
    if username is not None:
        users[ws] = '%s@%s' % (username, bottle.request.remote_addr)
    else:
        username = 'anonymous@%s' % bottle.request.remote_addr

    while True:
        try:
            msg = ws.receive()
            if msg is not None:
                logger.info('%s %s', username, msg)
            if username.startswith('anonymous@'):
                msg = { 'type': 'session', 'content': 'reconnect' }
                ws.send(json.dumps(msg))
            for item in queue:
                msg = { 'type': 'whatsapp', 'content': item.asDict() }
                for conn, user in users.items():
                    if user:
                        logger.info('user "%s", msg "%s"', user, msg)
                        conn.send(json.dumps(msg))
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
    bottle.run(
        app=app,
        host='0.0.0.0',
        port=8080,
        server=GeventWebSocketServer,
    )
except KeyboardInterrupt:
    print "Exit."
