class AST:
    pass


class Atom(AST):
    def __init__(self, word, ancillary_text=None):
        self.word = word
        self.ancillary_text = ancillary_text

    def __repr__(self):
        return 'Atom({}, ancillary_text={})'.format(repr(self.word), repr(self.ancillary_text))


class Then(AST):
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def __repr__(self):
        return 'Then({}, {})'.format(repr(self.a), repr(self.b))


class Else(AST):
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def __repr__(self):
        return 'Else({}, {})'.format(repr(self.a), repr(self.b))
