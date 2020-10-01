from model.state import *
import tkinter as tk

class BoardView(tk.Frame):

    def __init__(self, master, turn_box):
        super().__init__(master)
        self.turn_box = turn_box
        self.colors = {0: 'grey96', 1: "#FF6666", 2: "#6666FF"}
        self.basecolors = {1:"#FF2222", 2: "#2222FF"}

    def link_controller(self, controller):
        self.controller = controller
        rows = controller.cache.latest.rows
        cols = controller.cache.latest.cols
        #make the board
        self.tiles = [[None for j in range(cols)] for i in range(rows)]
        for i in range(rows):
            self.rowconfigure(i, weight=1)
        for j in range(cols):
            self.columnconfigure(j, weight=1)
        for i in range(rows):
            for j in range(cols):
                tile = Tile(self, (i, j))
                self.tiles[i][j] = tile
        self.set_view(controller.cache.latest)
        self.set_player(controller.cache.current_player)
        self.pack(fill='both', expand=1)

    def __getitem__(self, pos: Position):
        return self.tiles[pos[0]][pos[1]]

    def set_player(self, ply, win=False):
        self.turn_box['text'] = self.turn_box['text'] = 'player ' + str(ply)
        if win:
            self.turn_box['text'] += ' WINS!'

    def set_view(self, board: Board):
        for i in range(board.rows):
            for j in range(board.cols):
                cell = board[(i,j)]
                self.tiles[i][j].recolor(cell.player, cell.base)

class Tile(tk.Button):
    
    def __init__(self, master: BoardView, loc: Position):
        super().__init__(master, command=lambda:master.controller.tile_click(loc), overrelief='raised', relief='solid', bd=1)
        self.grid(row=loc[0], column=loc[1], sticky='nsew')
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0,weight=1) 
        self.bv = master

    def recolor(self, player, base):
        self['activebackground'] = self['bg'] = self.bv.colors[player]
        if base:
            self['activebackground'] = self['bg']  = self.bv.basecolors[player]

