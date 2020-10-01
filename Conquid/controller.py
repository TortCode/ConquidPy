from model.memory import *
from model.state import InvalidMove, Board

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
        if loc not in self.locs and board[loc].player == 0 and len(self.locs) < self.lim:
            ply = self.controller.cache.current_player
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
    vanquish_surround = [(-1,0), (-1,1), (-1,2), (-1,3),
                         (4,0), (4,1), (4,2), (4,3),
                         (0,-1), (1,-1), (2,-1), (3,-1),
                         (0,4), (1,4), (2,4), (3,4)]
    def __init__(self, controller: Controller):
        self.controller = controller
        self.done = False
    #null
    def propose(self):
        self.done = False
        return True

    def handle(self, corner):
        if self.done:
            return
        board = self.controller.cache.latest
        player = self.controller.cache.current_player
        #check that player surrounds square
        surrounding = 0
        for dx, dy in VanquishHandler.vanquish_surround:
            loc = (corner[0] + dx, corner[1] + dy)
            if board.is_valid_position(loc):
                cell = board[loc]
                if not cell.base and cell.player == player:
                    surrounding += 1
        if surrounding < 4:
            return
        # check that square is filled with enemy
        square_player = board[corner].player
        for dx, dy in Board.vanquish_offsets:
            loc = (corner[0] + dx, corner[1] + dy)
            if (not board.is_valid_position(loc)):
                return
            cell = board[loc]
            if (cell.base or cell.player != square_player):
                return
        # send command
        self.done = True
        self.controller.cache.receive(Move('V', self.controller.cache.current_player, corner=corner))
        self.controller.set_confirm(True)

class ConquestHandler:

    def __init__(self, controller: Controller):
        self.controller = controller

    def propose(self):
        try:
            self.controller.cache.receive(Move('Q', self.controller.cache.current_player))
            self.controller.set_confirm(True)
            return True
        except InvalidMove:
            return False

    #null
    def handle(self, loc):
        pass