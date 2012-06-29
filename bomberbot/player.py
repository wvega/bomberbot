#coding: utf-8


class Player(object):

    STAY = {'name': 'Stay', 'command': 'P'}
    MOVE_UP = {'name': 'Move Up', 'command': 'N'}
    MOVE_RIGHT = {'name': 'Move Right', 'command': 'E'}
    MOVE_DOWN = {'name': 'Move Down', 'command': 'S'}
    MOVE_LEFT = {'name': 'Move Left', 'command': 'O'}
    PUT_BOMB_UP = {'name': 'Put Bomb Up', 'command': 'BN'}
    PUT_BOMB_RIGHT = {'name': 'Put Bom Right', 'command': 'BE'}
    PUT_BOMB_DOWN = {'name': 'Put Bom Down', 'command': 'BS'}
    PUT_BOMB_LEFT = {'name': 'Put Bom Left', 'command': 'BO'}

    def __init__(self, name, x, y, alive=True):
        self.name = name
        self.alive = alive
        self.x = x
        self.y = y
