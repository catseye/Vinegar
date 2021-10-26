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
