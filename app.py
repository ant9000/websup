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
from cli.mail import Mailer
import os
import json


def here(path):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), path))

cfg = Config(here('configuration.ini'))
try:
    phone = cfg.get('whatsapp', 'phone')
    password = cfg.get('whatsapp', 'password')
    if not phone:
        raise NoOptionError('phone', 'whatsapp')
    if not password:
        raise NoOptionError('password', 'whatsapp')
except Exception, e:
    print """
ERROR: %s
Check file "configuration.ini" and make sure the Whatsapp
credentials are correct.

Use the command

  yowsup-cli registration help

for getting further help.
    """ % e
    sys.exit(1)

try:
    admin_username = cfg.get('webpage', 'username')
    admin_password = cfg.get('webpage', 'password')
    if not admin_username:
        raise NoOptionError('username', 'webpage')
    if not admin_password:
        raise NoOptionError('password', 'webpage')
    if admin_password == "admin":
        print "WARNING: please change the default web page credentials."
except Exception, e:
    print """
ERROR: %s
Check file "configuration.ini" and make sure the webpage
configuration is correct.
    """ % e
    sys.exit(2)

try:
    email_from = cfg.get('email', 'from')
    email_to = cfg.get('email', 'to')
    email_server = cfg.get('email', 'server')
    if not email_from:
        raise NoOptionError('from', 'email')
    if not email_to:
        raise NoOptionError('to', 'email')
    if not email_server:
        raise NoOptionError('server', 'email')
    mailer = Mailer(email_from, email_server)
except Exception, e:
    print """
ERROR: %s
Check file "configuration.ini" and make sure the email
configuration is correct.
    """ % e
    sys.exit(3)


logger = logging.getLogger()
queue = Queue()
stack = stack.WebsupStack((phone, password))
session_opts = {
    'session.cookie_expires': True,
    'session.auto': True,
}
app = SessionMiddleware(bottle.app(), session_opts)
web_clients = {}


def check_login(username, password):
    try:
        if username != '' and \
                username == admin_username and \
                password == admin_password:
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


@bottle.route('/websocket', apply=[websocket])
def echo(ws):
    session = bottle.request.environ.get('beaker.session', {})
    username = session.get('username', None)
    if username is not None:
        web_clients[ws] = '%s@%s' % (username, bottle.request.remote_addr)
    else:
        username = 'anonymous@%s' % bottle.request.remote_addr

    while True:
        try:
            msg = ws.receive()
            if msg is not None:
                logger.info('%s %s', username, msg)
            if username.startswith('anonymous@'):
                msg = {'type': 'session', 'content': 'reconnect'}
                ws.send(json.dumps(msg))
        except WebSocketError, e:
            logger.error(e)
            if ws in web_clients:
                del web_clients[ws]
            break


@bottle.route('/static/emoji/<filename:path>')
def send_static(filename):
    return bottle.static_file(filename, root=myemoji.EMOJI_STATIC_ROOT)


@bottle.route('/static/<filename:path>')
def send_static(filename):
    return bottle.static_file(filename, root=here('static'))


def yowsup():
    stack.start(queue)


def queue_consumer():
    while True:
        try:
            item = queue.peek(block=False)
            # send message via email
            subj = '[Whatsapp] new message from %s' % item.sender
            subj = unicode(subj).encode('utf-8')
            msg = bottle.template('email', item=item).encode('utf-8')
            mailer.send_email(email_to, subj, msg)
            # broadcast message to all connected clients
            if web_clients:
                msg = {'type': 'whatsapp', 'content': item.asDict()}
                for conn, user in web_clients.items():
                    if user:
                        logger.info('user "%s", msg from "%s" ', user, item.sender)
                        conn.send(json.dumps(msg))
            # work done, now we can consume message
            queue.get()
        except gevent.queue.Empty:
            pass
        except WebSocketError, e:
            logger.error(e)
            break
        gevent.sleep(0.5)


try:
    gevent.spawn(queue_consumer)
    gevent.spawn(yowsup)
    bottle.run(
        app=app,
        host='0.0.0.0',
        port=8080,
        server=GeventWebSocketServer,
    )
except KeyboardInterrupt:
    print "Exit."
