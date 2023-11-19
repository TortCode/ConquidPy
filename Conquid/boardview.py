from model.state import Board, Position
from controller import Controller
import tkinter as tk


class BoardView(tk.Frame):

    def __init__(self, master, turn_box):
        super().__init__(master)
        self.turn_box = turn_box
        self.colors = {0: 'grey96', 1: "#FF6666", 2: "#6666FF"}
        self.basecolors = {1: "#FF2222", 2: "#2222FF"}

    def setup(self, controller, rows, cols):
        # allow expansion to proper dimension
        for i in range(rows):
            self.rowconfigure(i, weight=1)
        for j in range(cols):
            self.columnconfigure(j, weight=1)
        self.pack(fill='both', expand=1, anchor='center')
        # fill board
        self.tiles = [[None for j in range(cols)] for i in range(rows)]
        for i in range(rows):
            for j in range(cols):
                tile = Tile(self, controller, (i, j))
                self.tiles[i][j] = tile

    def discard_tiles(self):
        for row in self.tiles:
            for tile in row:
                tile.destroy()

    def __getitem__(self, pos: Position):
        return self.tiles[pos[0]][pos[1]]

    def set_player(self, ply, win=False):
        self.turn_box['text'] = self.turn_box['text'] = 'PLAYER ' + str(ply)
        self.turn_box['text'] += ' WINS!' if win else ' TURN'

    def set_view(self, board: Board):
        for i in range(board.rows):
            for j in range(board.cols):
                cell = board[i, j]
                self.tiles[i][j].recolor(cell.player, cell.base)


class Tile(tk.Button):

    def __init__(self, master: BoardView,
                 controller: Controller, loc: Position):
        super().__init__(master,
                         command=lambda: controller.tile_click(loc),
                         overrelief='raised', relief='solid', bd=1)
        self.grid(row=loc[0], column=loc[1], sticky='nsew')

    def recolor(self, player, base):
        if base:
            self['bg'] = self.master.basecolors[player]
        else:
            self['bg'] = self.master.colors[player]
        self['activebackground'] = self['bg']
