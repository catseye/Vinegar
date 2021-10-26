from vinegar.ast import Atom, Then, Else


########## Parser ##########
#
# Program     ::= {Definition}.
# Definition  ::= name<def> "=" Expression ";".
# Expression  ::= Term {"|" Term}.
# Term        ::= Atom {Atom}.
# Atom        ::= "(" Expression ")" | name<use> [bracketedtext].
#

class ParseError(ValueError):
    pass


class Parser:
    def __init__(self, scanner, definitions):
        self.scanner = scanner
        self.definitions = definitions

    def program(self):
        while not self.scanner.on_type('EOF'):
            self.definition()
        return self.definitions

    def definition(self):
        name = self.scanner.token
        self.scanner.scan()
        self.scanner.expect('=')
        expr = self.expression()
        self.scanner.expect(';')
        self.definitions[name] = expr

    def expression(self):
        t1 = self.term()
        while self.scanner.consume('|'):
            t2 = self.term()
            t1 = Else(t1, t2)
        return t1

    def term(self):
        a1 = self.atom()
        while self.scanner.on_type('word'):
            a2 = self.atom()
            a1 = Then(a1, a2)
        return a1

    def atom(self):
        if self.scanner.consume('('):
            e = self.expression()
            self.scanner.expect(')')
            return e
        self.scanner.check_type('word')
        word = self.scanner.token
        self.scanner.scan()
        ancillary_text = None
        if self.scanner.on_type('bracketed_text'):
            ancillary_text = self.scanner.token
            self.scanner.scan()
        return Atom(word, ancillary_text=ancillary_text)
