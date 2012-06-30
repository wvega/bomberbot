#coding: utf-8

import random

from cell import Cell
from player import Player


class Map(object):

    BLOCK_WALL = 'L'
    BLOCK_UNDESTRUCTIBLE = 'X'
    BLOCK_EXPLOSION = '#'
    BLOCK_EMPTY = '_'

    BLOCK_TICKLING_BOMB_3 = '3'
    BLOCK_TICKLING_BOMB_2 = '2'
    BLOCK_TICKLING_BOMB_1 = '1'

    BLOCK_BOMB_RANGE = '='

    POWER_INCREASE_BOMBS = 'V'
    POWER_INCREASE_POWER = 'P'

    PLAYER_A = 'A'
    PLAYER_B = 'B'
    PLAYER_C = 'C'
    PLAYER_D = 'D'

    def __init__(self, description, player_name, target=None, bombs=1):
        self.map = []
        self.description = []
        self.players = {}
        self.target = target
        self.bombs = bombs

        self.parse(description)
        self.player = self.players.get(player_name, None)

        self.update()

    def parse(self, description):
        """
        Take a string represntation of the map and creates a matrix
        containing information about the kind of block in every position
        and the weight (cost) associated with moving to that position.
        """

        self.threats = []

        # fill grid with weights
        for i, r in enumerate(description.split('\n')):
            row = []
            for k, c in enumerate(r.split(",")):
                c = c.strip()
                if c == 'L':
                    cell = Cell.wall(k, i)
                elif c == 'X':
                    cell = Cell.undestructible(k, i)
                elif c == '#':
                    cell = Cell.explosion(k, i)
                elif c == '_':
                    cell = Cell.empty(k, i)
                elif c in ['1', '2', '3']:
                    cell = Cell.bomb(c, k, i)
                    self.threats.append(cell)
                elif c in ['V', 'P']:
                    cell = Cell.improvement(c, k, i)
                elif c in ['A', 'B', 'C', 'D']:
                    cell = Cell.player(c, k, i)
                    self.players.setdefault(c.upper(), Player(c, k, i, True))
                elif c in ['a', 'b', 'c', 'd']:
                    cell = Cell.player(c, k, i, False)
                    self.players.setdefault(c.upper(), Player(c, k, i, False))
                row.append(cell)
                self.description.append(c)
            self.map.append(row)

        # raw representation of the map, without spaces nor other characters
        self.description = ''.join(self.description)

    def update(self):
        """
        Scan the map looking for threats and update the cell weights.
        """
        steps = 3

        # print [c.kind for c in self.threats]
        for threat in self.threats:
            directions = {'UP': 1, 'RIGHT': 1, 'DOWN': 1, 'LEFT': 1}
            for s in range(1, steps + 1):
                for k, d in enumerate(directions):
                    if directions[d] == 0:
                        continue
                    cell = self.get_cell(threat.x, threat.y, s, d)
                    # print cell.kind, cell.x, cell.y, cell.weight
                    # print threat.x, threat.y, s, d, cell.kind
                    # block that prevent the bot from advancing in that direction
                    if cell.is_wall or cell.is_undestructible:
                        directions[d] = 0
                    # do not put traps behind the player, but increase cells' cost
                    # to alow user to turn instead of going back, when possible
                    elif cell.kind == self.player.name:
                        cell.weight = cell.weight + threat.weight
                        directions[d] = 2
                    # TODO: try replacing all cells with trap blocks
                    # blocks that can be replaced by bomb range blocks
                    elif (cell.is_empty or cell.is_improvement) and directions[d] == 1:
                        self.map[cell.y][cell.x] = Cell.trap(cell.x, cell.y, threat.weight, cell.parent)
                    else:
                        weight = 1 if directions[d] == 2 else threat.weight
                        cell.weight = cell.weight + weight
                # print '>', directions

    def measure(self, start):
        distances = [20000 for i in range(0, 121)]
        remaining = [start]

        # distance to current position is 0
        distances[start.y * 11 + start.x] = 0

        # used to sort lists of cells by the cost of traveling to that position
        def comparator(a, b):
            return cmp(distances[(a.y * 11) + a.x], distances[(b.y * 11) + b.x])

        while len(remaining) > 0:
            current = remaining.pop()
            a = (current.y * 11) + current.x

            cells = self.get_adjacent_cells(current.x, current.y)
            # print [(c.kind, distances[c.y * 11 + c.x]) for c in cells]

            for n, adjacent in enumerate(cells):
                b = (adjacent.y * 11) + adjacent.x

                if distances[b] > distances[a] + adjacent.weight:
                    distances[b] = distances[a] + adjacent.weight
                    adjacent.parent = current

                    # remaining.append(adjacent)
                    # print adjacent.x, adjacent.y, adjacent.kind, adjacent.is_empty, adjacent.is_wall, adjacent.is_improvement
                    if adjacent.is_empty or adjacent.is_wall or adjacent.is_improvement:
                        remaining.append(adjacent)
                # print "(%d, %d) -> (%d, %d) %d" % (current.x, current.y, adjacent.x, adjacent.y, distances[b])

            remaining = sorted(remaining, comparator)
            # print remaining

        return distances, comparator

    def next(self):
        """
        Returns the next action for a given Player in this map.

        We would like to move towards improvements and other players.
        """

        player = self.player
        start = self.get_cell(player.x, player.y)

        # calculate cost of moving
        distances, comparator = self.measure(start)

        # 5% probability of dropping previous target
        if self.target is not None and random.random() < 0.95:
            cells = self.find(lambda c: c.kind == self.target)
        else:
            cells = []

        improvements = self.find(lambda c: c.is_improvement)
        players = self.find(lambda c: c.is_player and c.kind != player.name)
        cells = cells + sorted(improvements + players, comparator)

        print 'Previous:', self.target
        print 'Targets:', [(c.kind, distances[c.y * 11 + c.x]) for c in cells]
        print 'Start:', start.kind, start.x, start.y, start.weight

        if len(cells) > 0:
            self.target = cells[0].kind

        action = self.choose(start, cells)
        print 1, action, start.weight
        # if we are on a bomb's range and the bot decided to stay, let's try to
        # to move to one of the adyacent cells to avoid explosion
        if (action is None or action is Player.STAY) and start.weight > 1.5:
            cells = sorted(self.get_adjacent_cells(start.x, start.y), comparator)
            action = self.choose(start, cells)
        if action is None:
            return Player.STAY
        print 2, action, start.weight
        return action

        # for y in range(0, 11):
        #     i = y * 11
        #     print distances[i:i+11]

        # no action, let's just stay here for a while

    def choose(self, start, cells):
        action = None
        for cell in cells:
            action = self.move(start, cell)
            if action is not None:
                print 'Target:', cell.kind, cell.x, cell.y, cell.weight
                break
        return action

    def move(self, start, target):
        """
        Given a start position and a target position find the right
        action/movement.
        """

        path = [target]
        next = None

        parent = target.parent
        while parent is not None and parent != start:
            path.append(parent)
            next = parent
            parent = parent.parent

        if parent is None:
            return Player.STAY
        elif next is None:
            next = target

        # block that prevents the bot from advancing in that direction
        if next.is_wall or next.is_undestructible or next.is_player:
            return None
        if next.is_bomb:
            return None

        if next.x == start.x:
            if next.y > start.y:
                action = Player.MOVE_DOWN
            elif next.y < start.y:
                action = Player.MOVE_UP
        elif next.y == start.y:
            if next.x > start.x:
                action = Player.MOVE_RIGHT
            elif next.x < start.x:
                action = Player.MOVE_LEFT

        # only reason for start cell to have a weight greater than 1.5
        # is that the cell is close to a tickling bomb. Let's move.
        if start.weight > 1.5:
            return action

        path.reverse()

        # if we are two blocks away from being in front of a player, let's put
        # a bomb with a probability of 40%
        if len(path) >= 3 and random.random() < 0.4:
            future = path[2]  # two steps ahead
            if not future.is_player:
                pass
            return self.attack(action)

        # if we are moving towards a wall or a player, let's put a bomb instead
        if len(path) >= 2:
            future = path[1]  # one step ahead
            if not future.is_player and not future.is_wall:
                return action
            return self.attack(action)

        return action

    def attack(self, action):
        if action == Player.MOVE_UP:
            return Player.PUT_BOMB_UP
        elif action == Player.MOVE_RIGHT:
            return Player.PUT_BOMB_RIGHT
        elif action == Player.MOVE_DOWN:
            return Player.PUT_BOMB_DOWN
        elif action == Player.MOVE_LEFT:
            return Player.PUT_BOMB_LEFT
        else:
            # TODO: try Staing instead
            return action

    def find(self, filter):
        cells = []
        for row in self.map:
            for cell in row:
                if filter(cell):
                    cells.append(cell)
        return cells

    def find_cells(self, kinds):
        """
        Return a list of cells of the given kinds.
        """

        cells = []

        for pos, char in enumerate(self.description):
            if char in kinds:
                y = pos / 11
                x = pos % 11
                cells.append(self.map[y][x])

        return cells

    def get_cell(self, x, y, steps=0, direction=None):
        if direction == 'UP':
            y = max(0, y - steps)
        if direction == 'RIGHT':
            x = min(10, x + steps)
        if direction == 'DOWN':
            y = min(10, y + steps)
        if direction == 'LEFT':
            x = max(0, x - steps)

        return self.map[y][x]

    def get_adjacent_cells(self, x, y):
        cells = []

        indexes = [(x, max(0, y - 1)), (x, min(10, y + 1)), (min(10, x + 1), y), (max(0, x - 1), y)]
        for xy in indexes:
            cells.append(self.map[xy[1]][xy[0]])

        return cells

    # def find_players(self):
    #     # find players positions
    #     players = [self.PLAYER_A, self.PLAYER_B, self.PLAYER_C, self.PLAYER_D]
    #     lowered = self.description.lower()

    #     for p in players:
    #         pos = lowered.find(p.lower())

    #         if pos == -1:
    #             continue

    #         y = pos / 11
    #         x = pos % 11
    #         player = Player(p, x, y, self.description[pos] == p.lower())

    #         self.add_player(player)

    # def add_player(self, player):
    #     return self.players.setdefault(player.name, player)

    def get_player(self, letter):
        return self.players.get(letter, None)

    def __repr__(self):
        rows = []
        for i, row in enumerate(self.map):
            columns = []
            for k, col in enumerate(row):
                columns.append(col.kind)
            rows.append('| %s |' % ','.join(columns))

        return '\n%s\n' % '\n'.join(rows)
