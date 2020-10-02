from model.memory import *
from model.state import *
from boardview import BoardView
from tkinter import messagebox

class Controller:

    def __init__(self):
        self.handlers = {}
        self.handlers['A'] = AcquireHandler(self, 3)
        self.handlers['C'] = ConquerHandler(self)
        self.handlers['V'] = VanquishHandler(self)
        self.handlers['Q'] = ConquestHandler(self)
        self.cache = None
        self.boardview = None

    def link_buttons(self, move_btns, undo, confirm, prev, pause_play, next):
        self.move_btns = move_btns
        self.undo_btn = undo
        self.confirm_btn = confirm
        self.prev_btn = prev
        self.pauseplay_btn = pause_play
        self.next_btn = next
        self.set_state('MOVE_BLANK')     

    def button_pressed(self, action):
        if self.state == 'MOVE_BLANK':
            if self.handlers[action].propose():
                self.move_attempt = action

    def tile_click(self, loc):
        if self.state == 'MOVE_START' or self.state == 'MOVE_END':
            self.handlers[self.move_attempt].handle(loc)

    def confirm(self):
        if self.state == 'MOVE_END':
            self.set_state('MOVE_BLANK')
            self.cache.confirm()

    def undo(self):
        """Reverts move and deselects move type"""
        self.cache.discard_change()
        self.set_state('MOVE_BLANK')
        
    def revoke(self):
        """Reverts move but keeps move type"""
        self.cache.discard_change()
        self.set_state('MOVE_START')

    def pauseplay(self):
        if self.state == 'HIST' and \
            self.cache.at_last_state(finish_allowed=False):
            self.set_state('MOVE_BLANK')
        elif self.state == 'MOVE_BLANK':
            self.set_state('HIST')

    def check_prevnext(self):
        self.prev_btn['state'] = 'disabled' if self.cache.at_first_state() else 'normal'
        self.next_btn['state'] = 'disabled' if self.cache.at_last_state() else 'normal'
        self.pauseplay_btn['state'] = 'normal' if self.cache.at_last_state(finish_allowed=False) else 'disabled'

    def next_board(self):
        if self.state == 'HIST':
            self.cache.play_forward()
            self.check_prevnext()

    def prev_board(self):
        if self.state == 'HIST':
            self.cache.play_back()
            self.check_prevnext()

    def game_won(self):
        self.set_state('HIST')
        messagebox.showinfo(message= f'PLAYER {3 - self.cache.current_player} WINS!')
        self.pauseplay_btn['state'] = 'disabled'

    def set_state(self, state: str):
        self.state = state
        if state == 'HIST':
            self.enter_limbo(reversible=False)
            self.check_prevnext()
            self.pauseplay_btn['text'] = 'play'
        else:
            self.prev_btn['state'] = 'disabled'
            self.next_btn['state'] = 'disabled'
            self.pauseplay_btn['text'] = 'pause'
        if state == 'MOVE_BLANK':
            self.move_attempt = ''
            self.exit_limbo()
        elif state == 'MOVE_START':
            self.enter_limbo()
        elif state == 'MOVE_END':
            self.enter_limbo(confirmable=True)

    def enter_limbo(self, reversible=True, confirmable=False):
        for btn in self.move_btns.values():
            btn['state'] = 'disabled'
        if reversible:
            self.undo_btn['state'] = 'normal'
            self.pauseplay_btn['state'] = 'disabled'
            if confirmable:
                self.confirm_btn['state'] = 'normal'
        else:
            self.pauseplay_btn['state'] = 'normal'
            self.undo_btn['state'] = 'disabled'
            self.confirm_btn['state'] = 'disabled' 

    def exit_limbo(self):
        for btn in self.move_btns.values():
            btn['state'] = 'normal'
        self.pauseplay_btn['state'] = 'normal'
        self.undo_btn['state'] = 'disabled'
        self.confirm_btn['state'] = 'disabled'

    

class AcquireHandler:

    def __init__(self, controller: Controller, limit):
        self.lim = limit
        self.locs = []
        self.controller = controller

    def propose(self):
        self.locs = []
        self.controller.set_state('MOVE_START')
        return True

    def handle(self, loc):
        board = self.controller.cache.latest
        ply = self.controller.cache.current_player
        if loc in self.locs:
            self.controller.revoke()
            self.locs.remove(loc)
            for tileloc in self.locs:
                self.controller.boardview[tileloc].recolor(ply, False)
        elif board[loc].player == 0 and len(self.locs) < self.lim:
            self.controller.boardview[loc].recolor(ply, False)
            self.locs.append(loc)
            if len(self.locs) == self.lim:
                self.controller.cache.receive(Move('A', ply, locs=self.locs))
                self.controller.set_state('MOVE_END')

class ConquerHandler:

    def __init__(self, controller: Controller):
        self.controller = controller

    def propose(self):
        self.controller.cache.receive(Move('C', self.controller.cache.current_player))
        self.controller.set_state('MOVE_END')
        return True
    #null
    def handle(self, loc):
        pass

class VanquishHandler:

    def __init__(self, controller: Controller):
        self.controller = controller
    #null
    def propose(self):
        self.controller.set_state('MOVE_START')
        return True

    def handle(self, corner):
        self.controller.revoke()
        # send command
        try:
            self.controller.cache.receive(Move('V', self.controller.cache.current_player, corner=corner))
            self.controller.set_state('MOVE_END')
        except InvalidMove:
            pass

class ConquestHandler:

    def __init__(self, controller: Controller):
        self.controller = controller

    def propose(self):
        try:
            self.controller.cache.receive(Move('Q', self.controller.cache.current_player))
        except InvalidMove:
            return False
        self.controller.set_state('MOVE_END')
        return True
    #null
    def handle(self, loc):
        pass