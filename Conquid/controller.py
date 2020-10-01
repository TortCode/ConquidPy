from model.memory import *
from model.state import *
from boardview import BoardView

class Controller:

    def __init__(self):
        self.handlers = {}
        self.handlers['A'] = AcquireHandler(self, 3)
        self.handlers['C'] = ConquerHandler(self)
        self.handlers['V'] = VanquishHandler(self)
        self.handlers['Q'] = ConquestHandler(self)

    def link_buttons(self, move_btns, undo, confirm, turnbox):
        self.move_btns = move_btns
        self.undo_btn = undo
        undo['state'] = 'disabled'
        self.confirm_btn = confirm
        confirm['state'] = 'disabled'
        self.turn_box = turnbox

    def load_history(self, history: History):
        self.move_attempt = ''
        self.state = 'MOVE_BLANK'
        self.cache = Cache(history, self)

    def link_boardview(self, boardview: 'Boardview'):
        self.bv = boardview
        self.cache.boardview = boardview

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
        self.cache.undo()
        self.set_state('MOVE_BLANK')
        
    def revoke(self):
        self.cache.undo()
        self.set_state('MOVE_START')

    def next_board(self):
        self.cache.play_forward()

    def prev_board(self):
        self.cache.play_back()

    def game_won(self):
        self.set_state('HIST')

    def set_state(self, state: str):
        self.state = state
        if state == 'HIST':
            self.enter_limbo(reversible=False)
        elif state == 'MOVE_BLANK':
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
        else:
            self.undo_btn['state'] = 'disabled'
        if confirmable:
            self.confirm_btn['state'] = 'normal'
        else:
            self.confirm_btn['state'] = 'disabled' 

    def exit_limbo(self):
        for btn in self.move_btns.values():
            btn['state'] = 'normal'
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
                self.controller.bv[tileloc].recolor(ply, False)
        elif board[loc].player == 0 and len(self.locs) < self.lim:
            self.controller.bv[loc].recolor(ply, False)
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