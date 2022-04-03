import math
from collections import deque
from heapq import heappush, heappop
from typing import Tuple
from functools import partial
Position = Tuple[int,int]

class Cell:
    """
    stores information about player and base status

    player = 0 if empty
    player = 1 or 2 respectively for player 1 or 2

    base = False if its a normal gameplay cell or it is the center of the base
    base = True if its in the 8 cell ring of the base surrounding the center
    """
    def __init__(self, player=0, base=False):
        self.player = player
        self.base = base

    def set_base(self, player):
        self.player = player
        self.base = True

    def copy(self):
        return Cell(**self.__dict__)

class Board:
    """
    A representation of the state of the game and its transformations
    To obtain a the cell at a particular location, call
        <board>[<position>]
    where:
    position is a pair of ints

    ***Note that the board is indexed from 0
       so the first coordinate may range from 0 to rows - 1
       and the second coordinate may range from 0 to cols - 1
    """
    adjacent_offsets = [(0,1),(0,-1),(1,0),(-1,0)]
    vanquish_offsets = [(i,j) for i in range(4) for j in range(4)]
    base_offsets3x3 = [(i,j) for i in range(-1,2) for j in range(-1,2)]
    base_offsets2x2 = [(0,0),(0,1),(1,0),(1,1)]
    vanquish_surround = [(-1,0), (-1,1), (-1,2), (-1,3),
                         (4,0), (4,1), (4,2), (4,3),
                         (0,-1), (1,-1), (2,-1), (3,-1),
                         (0,4), (1,4), (2,4), (3,4)]

    def __init__(self, r, c, base_size):
        self.rows = r
        self.cols = c
        self.grid = [[Cell() for j in range(c)] for i in range(r)]
        self.base_size = base_size
        if base_size == 2:
            self.bases = ((self.rows // 2 - 1, 4), (self.rows // 2 - 1, self.cols - 6))
            self.make_base2x2()
        elif base_size == 3:
            self.bases = ((self.rows // 2, 5), (self.rows // 2, self.cols - 6))
            self.make_base3x3()

    def make_base3x3(self):
        for player, center in enumerate(self.bases, 1):
            for dx, dy in Board.base_offsets3x3:
                self[center[0] + dx, center[1] + dy].set_base(player)
            self[center].base = False

    def make_base2x2(self):
        for player, corner in enumerate(self.bases, 1):
            for dx, dy in Board.base_offsets2x2:
                self[corner[0] + dx, corner[1] + dy].set_base(player)

    def copy(self):
        cpy = Board(self.rows, self.cols, self.base_size)
        for i in range(self.rows):
            for j in range(self.cols):
                cpy[i,j] = self[i,j].copy()
        return cpy

    def __getitem__(self, pos: Position) -> Cell:
        return self.grid[pos[0]][pos[1]]

    def __setitem__(self, pos: Position, value):
        self.grid[pos[0]][pos[1]] = value

    def is_valid_position(self, pos: Position):
        return pos[0] >= 0 and pos[0] < self.rows and pos[1] >= 0 and pos[1] < self.cols

    def adjacent(self, center: Position, base=False):
        for dx, dy in Board.adjacent_offsets:
            loc = (center[0] + dx, center[1] + dy)
            if self.is_valid_position(loc):
                if base or not self[loc].base:
                    yield loc

    def acquire(self, player, locs: [Position], validate=False):
        if validate:
            for loc in locs:
                if self[loc].player != 0:
                    raise InvalidMove
        for loc in locs:
            self[loc].player = player

    def conquer(self, player):
        enemy = 3 - player
        # player cells that touch enemy cell
        touching = [[0 for j in range(self.cols)] for i in range(self.rows)]
        # fill queue w player cells
        q = deque((i,j) for i in range(self.rows) for j in range(self.cols) \
            if self[i,j].player == player and not self[i,j].base)
        # begin teh konker
        while q:
            # newly conquered cell
            curr = q.popleft()
            for i, j in self.adjacent(curr):
                # update neighbour
                if self[i, j].player == enemy:
                    touching[i][j] += 1
                    if touching[i][j] >= 2:
                        #conquer neighbour
                        self[i, j].player = player
                        q.append((i,j))

    def vanquish(self, player, corner: Position, validate=False):
        #check that player surrounds square
        if validate:
            surrounding = 0
            for dx, dy in Board.vanquish_surround:
                loc = (corner[0] + dx, corner[1] + dy)
                if self.is_valid_position(loc):
                    cell = self[loc]
                    if not cell.base and cell.player == player:
                        surrounding += 1
            if surrounding < 4:
                raise InvalidMove()
        # check that square is filled with enemy
        square_player = self[corner].player
        square = []
        for dx, dy in Board.vanquish_offsets:
            loc = (corner[0] + dx, corner[1] + dy)
            if validate:
                if not self.is_valid_position(loc) or \
                    self[loc].base or \
                    self[loc].player != square_player:
                    raise InvalidMove()
            square.append(self[loc])
        # delete square
        for sq in square:
            sq.player = 0

    def conquest(self, player):
        enemy = 3-player
        # distance to player base
        dist = [[math.inf for j in range(self.cols)] for i in range(self.rows)]
        # is distance fixed
        visited = [[False for j in range(self.cols)] for i in range(self.rows)]
        # path from player base
        prev = [[None for j in range(self.cols)] for i in range(self.rows)]

        i, j = self.bases[player-1]
        start = (i,j)
        dist[i][j] = 0
        pq = [(0, start)]

        while pq:
            # current least-distance cell
            pathlen, curr = heappop(pq)
            visited[curr[0]][curr[1]] = True
            for i, j in self.adjacent(curr, base=True):
                if not visited[i][j] and self[i, j].player == player:
                    #update unvisited neighbours for shorter path
                    if dist[i][j] > pathlen + 1:
                        prev[i][j] = curr
                        dist[i][j] = pathlen + 1
                        heappush(pq, (dist[i][j], (i, j)))
                # trace path if found
                if self[i, j].base and self[i, j].player == enemy:
                    while curr != start:
                        self[curr].base = True
                        curr = prev[curr[0]][curr[1]]
                    return
        # no path found
        raise InvalidMove()

class Move:
    """
    A Command representing executable moves on the gameboard
    The format for creating a Move is as below:
    Acquire:
        Move('A', <player>, locs=<list of positions to be acquired>)

    Conquer:
        Move('C', <player>)

    Vanquish:
        Move('V', <player>, corner=<position of upper-left corner of 4x4 square to be deleted>)
    
    Conquest:
        Move('Q', <player>)

    where:
        player is 1 or 2
        position is a pair of ints
    """
    def __init__(self, type, player, locs=None, corner=None):
        self.type = type
        self.player = player
        if type == 'A':
            self.locs = locs
        if type == 'V':
            self.corner = corner

    def __call__(self, board: Board, *, validate=False):
        b = board.copy()
        if self.type == 'A':
            func = partial(b.acquire, validate=validate)
        if self.type == 'C':
            func = b.conquer
        if self.type == 'V':
            func = partial(b.vanquish, validate=validate)
        if self.type == 'Q':
            func = b.conquest
        func(player=self.player, locs=self.locs, corner=self.corner)
        return b

class InvalidMove(Exception):
    pass
