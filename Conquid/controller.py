from model.memory import *
from model.state import *

class Controller:

    def __init__(self, history: History, boardview: BoardView):
        self.move_attempt = ''
        self.bv = boardview
        self.cache = Cache(history, boardview)
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

    def button_pressed(self, action):
        if self.handlers[action].propose():
            self.move_attempt = action
            self.enter_limbo()
            self.handlers[self.move_attempt].propose()

    def confirm(self):
        self.move_attempt = ''
        self.exit_limbo()
        if self.cache.confirm():
            self.enter_limbo(reversible=False)
        else:
            self.turn_box['text'] = 'player ' + str(self.cache.current_player)

    def undo(self):
        self.move_attempt = ''
        self.exit_limbo()
        self.cache.undo()

    def revoke(self):
        self.cache.undo()
        self.set_confirm(False)

    def enter_limbo(self, reversible=True):
        for btn in self.move_btns.values():
            btn['state'] = 'disabled'
        if reversible:
            self.undo_btn['state'] = 'normal'
        
    def set_confirm(self, allowable):
        if allowable:
            self.confirm_btn['state'] = 'normal'
        else:
            self.confirm_btn['state'] = 'disabled' 

    def exit_limbo(self):
        for btn in self.move_btns.values():
            btn['state'] = 'normal'
        self.undo_btn['state'] = 'disabled'
        self.confirm_btn['state'] = 'disabled'

    def tile_click(self, loc):
        if self.move_attempt:
            self.handlers[self.move_attempt].handle(loc)

class AcquireHandler:

    def __init__(self, controller: Controller, limit):
        self.lim = limit
        self.locs = []
        self.controller = controller

    def propose(self):
        self.locs = []
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
                self.controller.set_confirm(True)

class ConquerHandler:

    def __init__(self, controller: Controller):
        self.controller = controller

    def propose(self):
        self.controller.cache.receive(Move('C', self.controller.cache.current_player))
        self.controller.set_confirm(True)
        return True
    #null
    def handle(self, loc):
        pass

class VanquishHandler:

    def __init__(self, controller: Controller):
        self.controller = controller
    #null
    def propose(self):
        return True

    def handle(self, corner):
        self.controller.revoke()
        # send command
        try:
            self.controller.cache.receive(Move('V', self.controller.cache.current_player, corner=corner))
            self.done = True
            self.controller.set_confirm(True)
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
        self.controller.set_confirm(True)
        return True
    #null
    def handle(self, loc):
        pass