from model.state import *

class History:
    """
    Represents the entire history of moves and board states in a game
    To obtain a list of Boards in a game, call
        <history>.board__history()
    To obtain a list of Moves in game, call
        <history>.move__history()

    ***Remember, if a board is the (i)th state in the board history,
    then the last move done is the (i-1)th action in the move history
    """
    def __init__(self, rows: int, cols: int, base_size: int, moves=None):
        self.rows = rows
        self.cols = cols
        self.base_size = base_size
        self.moves = moves if moves else []

    def store(self, move: Move):
        self.moves.append(move.__dict__)

    def is_finished(self) -> bool:
        return self.moves and self.moves[-1]['type'] == 'Q'

    def move_history(self) -> [Move]:
        return [Move(**mv) for mv in self.moves]

    def board_history(self) -> [Board]:
        # starting state
        boards = [Board(self.rows, self.cols, self.base_size)]
        for mv in self.moves:
            boards.append(Move(**mv)(boards[-1]))
        return boards

class Cache:
    """
    Stores the current Board state and current player.
    For a move to be executed, entered into history, and the turn to change, the following calls must be made:

    1.  <cache>.receive(<move>) must be provided with a move to execute.
        It is possible for the move to be invalid, in which case it will be rejected and
        an InvalidMove exception will be raised from the method.

    2.  Once a valid move is entered, it may be undone by calling <cache>.undo()
        If ones wishes to confirm the move and begin the next turn, call <cache>.confirm()
        If the confirmed move is a valid conquest, confirm method will return a value of True
        to indicate the game is won by the current player

    The BoardView class must have a method with signature
        BoardView.set_view(self, <board>)
    thru which it receives updated boards to be displayed

    The BoardView class must also have a method with signature
        BoardView.set_player(self, <player>, win=False)
    thru which it receives the current player whose turn it is and whether they won yet.
    """
    def __init__(self, history: History):
        self.hist = history
        self.save = history.board_history()
        self.nstate = len(self.save) - 1
        self.current_player = self.nstate % 2 + 1
        self.latest = self.save[-1].copy()
        self.move = None 

    def link_gui(self, controller: 'Controller', boardview: 'Boardview'):
        self.controller = controller
        self.boardview = boardview
        controller.load_cache(self)
        boardview.set_view(self.latest)
        self.send_turn_status()

    def at_last_state(self, finish_allowed: bool = True) -> bool:
        return self.nstate == len(self.save)-1 and \
            (finish_allowed or not self.hist.is_finished())

    def at_first_state(self) -> bool:
        return self.nstate == 0

    def send_turn_status(self):
        if self.at_last_state() and self.hist.is_finished():
            self.boardview.set_player(3 - self.current_player, win=True)
        else:
            self.boardview.set_player(self.current_player)

    def play_back(self):
        if self.nstate > 0:
            self.nstate -= 1
            self.current_player = 3 - self.current_player
        self.boardview.set_view(self.save[self.nstate])
        self.send_turn_status()

    def play_forward(self):
        if self.nstate < len(self.save)-1:
            self.nstate += 1
            self.current_player = 3 - self.current_player
        self.boardview.set_view(self.save[self.nstate])
        self.send_turn_status()

    def receive(self, move: Move):
        if self.move or self.hist.is_finished():
            return
        self.latest = move(self.latest, validate=True)
        self.boardview.set_view(self.latest)
        self.move = move

    def discard_change(self):
        self.latest = self.save[-1]
        self.boardview.set_view(self.latest)
        self.move = None

    def confirm(self):
        if not self.move:
            return
        self.save.append(self.latest)
        self.hist.store(self.move)
        self.nstate += 1
        self.current_player = 3 - self.current_player
        if self.move.type == 'Q':
            self.controller.game_won()
        self.send_turn_status()
        self.move = None
