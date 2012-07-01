#coding: utf-8

import socket
import sys

from datetime import datetime
from exceptions import KeyboardInterrupt

from map import Map


class BomberBot(object):

    def __init__(self):
        self.retry = True
        self.maps = []

    def start(self):
        try:
            while self.retry:
                self.connect("wvega", "4feb56401b06eeff15002518")
                self.standby()
        except KeyboardInterrupt:
            print "\n\nGoodbay!"
            self.disconnect()
        except IOError as e:
            print e
            self.restart()

    def restart(self):
        self.disconnect()
        self.start()

    def connect(self, username, token):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)
        self.client.connect(("bomberbot.com", 5000))

        message = self.client.recv(4096)
        while message.find('Ingrese usuario y token:') == -1:
            message = message + self.client.recv(4096)

        print message
        print "Username: %s, Token: %s\n\n" % (username, token.replace(r'0', '*'))

        self.client.send("%s,%s" % (username, token))
        self.connected = True

    def disconnect(self):
        try:
            self.client.shutdown(socket.SHUT_RDWR)
            self.client.close()
        except IOError:
            pass

    def standby(self):
        unknown = 0
        print 'Waiting to join a game...'

        while self.connected:
            message = self.client.recv(2048)
            parts = message.split(";")

            if parts[0] == "EMPEZO":
                self.name = parts[2].strip()
                self.update(parts[1], True)
                print 'Bot just joined a new game as player %s.' % self.name
                unknown = 0

            elif parts[0] == "PERDIO":
                print("Bot %s has been aggressively destroyed. I'm afraid you just lost :(." % self.name)
                unknown = 0

            elif parts[0] == "TURNO":
                turn = parts[1]
                self.update(parts[2])
                print("\nNow playing turn %s [%s]\n" % (turn, datetime.now()))
                action = self.next()
                self.client.send(action['command'])
                print self.maps[-1]
                print("Bot %s will %s (%s)." % (self.name, action['name'], action['command']))
                unknown = 0

            else:
                if unknown >= 1000:
                    print 'A thousand unknown messages received. Quiting.'
                    self.disconnect()
                    return
                unknown = unknown + 1

    def update(self, description, reset=False):
        if reset:
            self.maps = []

        # keep only the last three maps
        if len(self.maps) >= 3:
            self.maps.pop(0)

        if len(self.maps) > 0:
            map = self.maps[-1]
            target = map.target
        else:
            target = None

        map = Map(description, self.name, target)
        self.maps.append(map)
        # print map

    def next(self):
        # grab most recent map
        map = self.maps[-1]
        # calculate *best* action
        return map.next()
