#coding: utf-8


class Cell(object):

    INCREASE_BOMBS = 'V'
    INCREASE_POWER = 'P'

    PLAYER_A = 'A'
    PLAYER_B = 'B'
    PLAYER_C = 'C'
    PLAYER_D = 'D'

    EMPTY = '_'
    WALL = 'L'

    TICKLING_BOMB_3 = '3'
    TICKLING_BOMB_2 = '2'
    TICKLING_BOMB_1 = '1'
    BOMB_RANGE = '='
    EXPLOSION = '#'

    UNDESTRUCTIBLE = 'X'

    def __init__(self, kind, x, y, weight, parent=None):
        self.kind = kind
        self.x = x
        self.y = y
        self.weight = weight
        self.parent = parent

        self.is_improvement = False
        self.is_player = False
        self.is_empty = False
        self.is_wall = False
        self.is_bomb_range = False
        self.is_undestructible = False

    @classmethod
    def improvement(cls, improvement, x, y, parent=None):
        if improvement == 'V':
            kind = cls.INCREASE_BOMBS
        elif improvement == 'P':
            kind = cls.INCREASE_POWER
        block = Cell(kind, x, y, 1, parent)
        block.is_improvement = True
        return block

    @classmethod
    def player(cls, name, x, y, alive=True, parent=None):
        name = name.upper()

        if name == 'A':
            kind = cls.PLAYER_A
        elif name == 'B':
            kind = cls.PLAYER_B
        elif name == 'C':
            kind = cls.PLAYER_C
        elif name == 'D':
            kind = cls.PLAYER_D

        block = Cell(kind, x, y, 1.5 if alive else 2, parent)
        block.is_player = alive

        return block

    @classmethod
    def empty(cls, x, y, parent=None):
        block = Cell(cls.EMPTY, x, y, 2, parent)
        block.is_empty = True
        return block

    @classmethod
    def wall(cls, x, y, parent=None):
        block = Cell(cls.WALL, x, y, 8, parent)
        block.is_wall = True
        return block

    @classmethod
    def bomb(cls, time, x, y, parent=None):
        if time == '1':
            kind = cls.TICKLING_BOMB_1
            weight = 66
        elif time == '2':
            kind = cls.TICKLING_BOMB_2
            weight = 64
        elif time == '3':
            kind = cls.TICKLING_BOMB_3
            weight = 62
        block = Cell(kind, x, y, weight, parent)
        return block

    @classmethod
    def trap(cls, x, y, weight, parent=None):
        block = Cell(cls.BOMB_RANGE, x, y, weight, parent)
        block.is_bomb_range = True
        return block

    @classmethod
    def explosion(cls, x, y, parent=None):
        block = Cell(cls.EXPLOSION, x, y, 100, parent)
        return block

    @classmethod
    def undestructible(cls, x, y, parent=None):
        block = Cell(cls.UNDESTRUCTIBLE, x, y, 10000, parent)
        block.is_undestructible = True
        return block
