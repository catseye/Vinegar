import re
import sys

########## Scanner ##########

class Scanner(object):
    def __init__(self, text):
        self.text = text
        self.token = None
        self.type = None
        self.pos = 0
        self.scan()

    def near_text(self, length=10):
        return self.text[self.pos:self.pos + length]

    def scan_pattern(self, pattern, type, token_group=1):
        pattern = r'(' + pattern + r')'
        regexp = re.compile(pattern, flags=re.DOTALL)
        match = regexp.match(self.text, pos=self.pos)
        if not match:
            return False
        else:
            self.type = type
            self.token = match.group(token_group)
            self.pos += len(match.group(1))
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
        if self.scan_pattern(r'\(|\)|\{|\}', 'bracket'):
            return
        if self.scan_pattern(r'\[(.*?)\]', 'bracketed_text', token_group=2):
            return
        if self.scan_pattern(r"[a-zA-Z_]['a-zA-Z0-9_-]*", 'word'):
            return
        if self.scan_pattern(r'.', 'unknown character'):
            return
        else:
            raise AssertionError("this should never happen, self.text=({}), self.pos=({})".format(self.text, self.pos))

    def expect(self, token):
        if self.token == token:
            self.scan()
        else:
            raise ParseError("Expected '{}', but found '{}' (near '{}')".format(
                token, self.token, self.near_text()
            ))

    def on(self, *tokens):
        return self.token in tokens

    def on_type(self, *types):
        return self.type in types

    def check_type(self, *types):
        if not self.on_type(*types):
            raise ParseError("Expected {}, but found {} ('{}') (near '{}')".format(
                types, self.type, self.token, self.near_text()
            ))

    def consume(self, *tokens):
        if self.token in tokens:
            self.scan()
            return True
        else:
            return False

########## AST ##########

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


class Result:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return '{}({})'.format(self.__class__.__name__, self.value)


class Failure(Result):
    pass


class OK(Result):
    pass


def b_swap(stack, **kwargs):
    if len(stack) < 2:
        return Failure('underflow')
    n = stack[:]
    a = n[-1]
    n[-1] = n[-2]
    n[-2] = a
    return OK(n)


def b_push(stack, ancillary_text=None):
    try:
        n = stack[:]
        n.append(int(ancillary_text))
        return OK(n)
    except Exception as e:
        return Fail(str(e))


BUILTINS = {
    'swap': b_swap,
    'push': b_push,
}


def interpret(definitions, stack, expr):
    # print('>>> {}'.format(expr))
    if isinstance(expr, Atom):
        entry = definitions[expr.word]
        if callable(entry):
            return entry(stack, ancillary_text=expr.ancillary_text)
        else:
            return interpret(definitions, stack, entry)
    elif isinstance(expr, Then):
        result = interpret(definitions, stack, expr.a)
        if isinstance(result, OK):
            stack = result.value
            return interpret(definitions, stack, expr.b)
        elif isinstance(result, Failure):
            return result
        else:
            raise NotImplementedError(result)
    elif isinstance(expr, Else):
        result = interpret(definitions, stack, expr.a)
        if isinstance(result, OK):
            return result
        elif isinstance(result, Failure):
            # TODO push the Failure onto the stack...
            return interpret(definitions, stack, expr.b)
        else:
            raise NotImplementedError(result)
    else:
        raise NotImplementedError('Expected atom or operation, got {}'.format(expr))


def main():
    program_text = sys.stdin.read()
    scanner = Scanner(program_text)
    parser = Parser(scanner, BUILTINS.copy())
    definitions = parser.program()
    # print(definitions['main'])
    s = interpret(definitions, [], definitions['main'])
    print(s)


if __name__ == '__main__':
    main()
