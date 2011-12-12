#!/usr/bin/env python
# coding: utf-8
# Wentao Han <wentao.han@gmail.com>

"""
A terminal XMPP chat program.

Usage: chat.py [options]

Options:
  -h, --help            show this help message and exit
  --debug               log debug information to file
  -j JID, --jid=JID     JID to use
  -p PASSWORD, --password=PASSWORD
                        password to use

Commands:
    /msg <who> <text>   send message and save target, so next time you just
                        need to type message itself to send
    /quit               exit from XMPPii
"""

import curses
import getpass
import locale
import logging
import optparse
import sys
import time

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

import sleekxmpp

# Set locale to make Unicode character correctly displayed under curses
locale.setlocale(locale.LC_ALL, '')

SIMPLE_TIMESTAMP_FORMAT = '%Y-%m-%d %H:%M:%S'
COMMAND_PREFIX = '/'

def time_string():
    return time.strftime(SIMPLE_TIMESTAMP_FORMAT)


class Console:
    """A console consisted of two parts."""

    def __init__(self):
        self.stdscr = curses.initscr()
        h, w = self.stdscr.getmaxyx()
        self.stdscr.hline(h - 2, 0, '-', w)
        self.stdscr.refresh()
        self.display_win = self.stdscr.derwin(h - 2, w, 0, 0)
        self.display_win.scrollok(True)
        self.input_win = self.stdscr.derwin(1, w, h - 1, 0)
        self.input_win.scrollok(True)

    def end(self):
        curses.endwin()

    def printf(self, format, *args, **kwargs):
        if args:
            message = format % args
        elif kwargs:
            message = format % kwargs
        else:
            message = format
        self.display_win.addstr(message)
        self.display_win.refresh()
        self.input_win.refresh()

    def gets(self):
        # TODO: add readline-like function
        # FIXME: multibyte character not deleted entirely
        return self.input_win.getstr()


class ChatClient(sleekxmpp.ClientXMPP):
    """XMPP chat client."""

    def __init__(self, jid, password, console):
        super(ChatClient, self).__init__(jid, password)
        self.console = console
        self.add_event_handler('session_start', self.start)
        self.add_event_handler('message', self.message)

    def start(self, event):
        self.send_presence()
        self.get_roster()
        self.console.printf('done.\n')

    def message(self, msg):
        body = msg['body']
        if type(body) is unicode:
            body = body.encode('utf-8')
        buf = StringIO(body)
        first = True
        for line in buf:
            line = line.rstrip('\r\n')
            if first:
                first = False
                self.console.printf('%s %-10.10s> %s\n', time_string(), msg['from'], line)
            else:
                self.console.printf('                              > %s\n', line)

def main(argv):
    parser = optparse.OptionParser()
    parser.add_option('--debug',
                      help='log debug information to file',
                      action='store_const',
                      dest='loglevel',
                      const=logging.DEBUG,
                      default=logging.CRITICAL,
                     )
    parser.add_option('-j', '--jid',
                      help='JID to use',
                      dest='jid',
                     )
    parser.add_option('-p', '--password',
                      help='password to use',
                      dest='password',
                     )
    opts, args = parser.parse_args()

    logging.basicConfig(datefmt=SIMPLE_TIMESTAMP_FORMAT,
                        filename='chat.log',
                        format='%(asctime)s %(levelname)1.1s|%(message)s',
                        level=opts.loglevel,
                       )
    jid = opts.jid or raw_input('JID: ')
    password = opts.password or getpass.getpass('Password: ')

    try:
        console = Console()
        console.printf('%s = Initializing...', time_string())
        client = ChatClient(jid, password, console)
        if client.connect():
            client.process()
        last_to = None
        while True:
            text = console.gets()
            if text.startswith(COMMAND_PREFIX):
                text = text[len(COMMAND_PREFIX):]
                pos = text.find(' ')
                command = text[:pos] if pos != -1 else text
                text = text[pos + 1:]
                if command == 'quit':
                    break
                elif command == 'msg':
                    pos = text.find(' ')
                    to = text[:pos] if pos != -1 else text
                    text = text[pos + 1:]
                    if to:
                        last_to = to
            if text and last_to:
                console.printf('%s %-10.10s< %s\n', time_string(), last_to, text)
                client.send_message(
                    mto=last_to,
                    mbody=text,
                    mtype='chat',
                )
        console.printf('%s = Exiting...' % time_string())
        client.disconnect(wait=True)
        console.printf('done.\n')
    finally:
        console.end()

if __name__ == '__main__':
    sys.exit(main(sys.argv))
