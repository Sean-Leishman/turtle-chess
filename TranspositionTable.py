from Zobrist import Zobrist, POLYGLOT_RANDOM_ARRAY

class TranspositionTable(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(TranspositionTable, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.keylist = {}
        self.hasher = Zobrist(POLYGLOT_RANDOM_ARRAY)

    def __getitem__(self, board):
        try:
            currentkey = self.hasher(board)
            return self.keylist[currentkey]
        except KeyError:
            return None

    def put(self, board, value, legal_moves=None):
        currentkey = self.hasher(board)
        self.keylist[currentkey] = Node(value, legal_moves)

    def update(self, board, value=None, legal_moves=None):
        currentkey = self.hasher(board)
        self.keylist[currentkey].update(value, legal_moves)

    def clear(self):
        self.keylist = {}


class Node():
    def __init__(self, value, legal_moves=[]):
        self.value = value
        self.legal_moves = legal_moves

    def update(self, value=None, legal_moves=None):
        if value is None:
            self.value = self.value
        else:
            self.value = value
        if legal_moves is None:
            self.legal_moves = self.legal_moves
        else:
            self.legal_moves = legal_moves