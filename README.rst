XMPPii
======

XMPPii is a terminal XMPP chat program.

Setup
-----

You need to install SleekXMPP and dnspython packages before using XMPPii.

Usage
-----

::

    Usage: chat.py [options]
    
    Options:
      -h, --help            show this help message and exit
      --debug               log debug information to file
      -j JID, --jid=JID     JID to use
      -p PASSWORD, --password=PASSWORD
                            password to use

Commands
--------

::

    /msg <who> <text>   send message and save target, so next time you just
                        need to type message itself to send
    /quit               exit from XMPPii
