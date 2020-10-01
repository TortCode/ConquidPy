class Move:

    def __init__(self, type, player, **kwargs):
        self.type = type
        self.player = player
        if type == 'A':
            self.locs = kwargs['locs']
        if type == 'V':
            self.corner = kwargs['corner']

    def execute(self, board):
        if self.type == 'A':
            func = board.acquire
        if self.type == 'C':
            func = board.conquer
        if self.type == 'V':
            func = board.vanquish
        if self.type == 'Q':
            func = board.conquest
        func(**{k:v for k,v in self.__dict__.items() if k != 'type'})