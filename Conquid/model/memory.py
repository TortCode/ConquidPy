from boardview import BoardView
from model.state import Board
from model.move import Move

class History:
    def __init__(self, rows, cols, bases):
        self.rows = rows
        self.cols = cols
        self.bases = bases
        self.moves = []

    def store(self, move):
        self.moves.append(move.__dict__)

    @staticmethod
    def to_move(dct):
        return Move(**dct)

    def board_history(self):
        # starting state
        board = Board(self.rows, self.cols, self.bases)
        # update boards with moves to generate list
        boards = [board.copy()]
        for movedict in self.moves:
            Move(**movedict).execute(board)
            boards.append(board.copy())
        return boards

class Cache:
    
    def __init__(self, history: History, boardview: BoardView):
        self.hist = history
        self.current_player = 1
        self.latest = history.board_history()[0]
        self.save = self.latest.copy()
        self.move = None
        self.bv = boardview

    def receive(self, move: Move):
        if not self.move:
            move.execute(self.latest)
            self.bv.set_board(self.latest)
            self.move = move

    def undo(self):
        if self.move:
            self.latest = self.save.copy()
            self.bv.set_board(self.latest)
            self.move = None

    def confirm(self):
        if self.move:
            self.save = self.latest.copy()
            self.hist.store(self.move)
            self.move = None
            if self.move.type != 'Q':
                self.current_player = 3 - self.current_player
