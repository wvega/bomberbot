#coding: utf-8

import socket
import sys

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
        # except:
        #     print "\n\nWTF?"
        #     print sys.exc_traceback

    def connect(self, username, token):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(("bomberbot.com", 5000))

        message = self.client.recv(4096)
        while message.find('Ingrese usuario y token:') == -1:
            message = message + self.client.recv(4096)

        print message
        print "Username: %s, Token: %s\n\n" % (username, token.replace(r'0', '*'))

        self.client.send("%s,%s" % (username, token))
        self.connected = True

    def disconnect(self):
        self.client.close()

    def standby(self):
        print 'Waiting to join a game...'

        while self.connected:
            message = self.client.recv(2048)
            message = message.split(";")

            if message[0] == "EMPEZO":
                self.name = message[2][0]
                self.update(message[1])
                print 'Bot just joined a new game as player %s.' % self.name

            elif message[0] == "PERDIO":
                print("Bot %s has been aggressively destroyed. I'm afraid you just lost :(." % self.name)
                self.disconnect()
                return

            elif message[0] == "TURNO":
                turn = message[1]
                self.update(message[2])
                action = self.next()
                print("\nNow playing turn %s:" % turn)
                print("Bot %s will %s (%s)." % (self.name, action['name'], action['command']))
                print self.maps[-1]
                self.client.send(action['command'])

            else:
                print 'Unknown message received from server:\n%s' % message[0]
                print("Bot %s will %s (%s)." % (self.name, 'Stay', 'P'))
                self.client.send('P')
                # # something went wrong, let's just die
                # print("Oops. We screwed it. Run!:\n:%s" % message[0])
                # self.retry = False
                # self.disconnect()
                # return

    def update(self, description):
        # keep only the last three maps
        if len(self.maps) >= 3:
            self.maps.pop(0)
            previous = self.maps[-1]
            target = previous.target
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
