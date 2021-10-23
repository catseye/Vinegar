import re
import sys

class Scanner(object):
    def __init__(self, text):
        self.text = text
        self.token = None
        self.type = None
        self.pos = 0
        self.scan()

    def near_text(self, length=10):
        return self.text[self.pos:self.pos + length]

    def scan_pattern(self, pattern, type, token_group=1, rest_group=2):
        pattern = r'(' + pattern + r')'
        regexp = re.compile(pattern, flags=re.DOTALL)
        match = regexp.match(self.text, pos=self.pos)
        if not match:
            return False
        else:
            self.type = type
            self.token = match.group(token_group)
            self.pos += len(self.token)
            return True

    def scan(self):
        self.scan_pattern(r'[ \t\n\r]*', 'whitespace')
        while self.scan_pattern(r'\/\/.*?[\n\r]', 'comment'):
            self.scan_pattern(r'[ \t\n\r]*', 'whitespace')
        if self.pos >= len(self.text):
            self.token = None
            self.type = 'EOF'
            return
        if self.scan_pattern(u'\\|', 'operator'):
            return
        if self.scan_pattern(r'\;', 'punct'):
            return
        if self.scan_pattern(r'\(|\)|\{|\}|\[|\]', 'bracket'):
            return
        if self.scan_pattern(r"[a-zA-Z_]['a-zA-Z0-9_-]*", 'word'):
            return
        if self.scan_pattern(r'.', 'unknown character'):
            return
        else:
            raise AssertionError("this should never happen, self.text=(%s), self.pos=(%s)" % (self.text, self.pos))

    def expect(self, token):
        if self.token == token:
            self.scan()
        else:
            raise SyntaxError(u"Expected '%s', but found '%s' (near '%s')" %
                              (token, self.token, self.near_text()))

    def on(self, *tokens):
        return self.token in tokens

    def on_type(self, *types):
        return self.type in types

    def check_type(self, *types):
        if not self.on_type(*types):
            raise SyntaxError(u"Expected %s, but found %s ('%s') (near '%s')" %
                              (types, self.type, self.token, self.near_text()))

    def consume(self, *tokens):
        if self.token in tokens:
            self.scan()
            return True
        else:
            return False


#
# Program     ::= {Definition}.
# Definition  ::= Name<def> "=" Expression ";".
# Expression  ::= Term {"|" Term}.
# Term        ::= Atom {Atom}.
# Atom        ::= "(" Expression ")" | Name<use>.
#

class ParseError(ValueError):
    pass


class Parser:
    def __init__(self, scanner):
        self.scanner = scanner
        self.definitions = {}

    def program(self):
        while not self.scanner.on_type('EOF'):
            self.definition()
        return self.definitions

    def definition(self):
        name = self.scanner.token
        if name in self.definitions:
            raise ParseError('Name "{}" already defined'.format(name))
        self.scanner.scan()
        self.scanner.expect('=')
        expr = self.expression()
        self.scanner.expect(';')
        self.definitions[name] = expr

    def expression(self):
        alts = ['|']
        t = self.term()
        alts.append(t)
        while self.scanner.consume('|'):
            t = self.term()
            alts.append(t)
        return alts

    def term(self):
        thens = ['&']
        a = self.atom()
        thens.append(a)
        while self.scanner.on_type('word'):
            a = self.atom()
            thens.append(a)
        return thens

    def atom(self):
        if self.scanner.consume('('):
            e = self.expression()
            self.scanner.expect(')')
            return e
        self.scanner.check_type('word')
        word = self.scanner.token
        self.scanner.scan()
        return word


def interpret(definitions, stack, expr):
    # print('>>> {}'.format(expr))
    if isinstance(expr, str):
        return interpret(definitions, stack, definitions[expr])
    elif isinstance(expr, list):
        if expr[0] == '&':
            for elem in expr[1:]:
                stack = interpret(definitions, stack, elem)
            return stack
        elif expr[0] == '|':
            try:
                stack = interpret(definitions, stack, expr[1])
            except Exception as e:
                return stack + [e]
            return stack
        else:
            raise NotImplementedError('Expected & or |')
    else:
        raise NotImplementedError('Expected atom or operation')


def main():
    program_text = sys.stdin.read()
    scanner = Scanner(program_text)
    parser = Parser(scanner)
    definitions = parser.program()
    print(definitions)
    s = interpret(definitions, [], 'main')
    print(s)

if __name__ == '__main__':
    main()
