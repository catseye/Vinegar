import sys

from vinegar.scanner import Scanner
from vinegar.parser import Parser
from vinegar.interpreter import interpret, BUILTINS


def main(args):
    program_text = sys.stdin.read()
    scanner = Scanner(program_text)
    parser = Parser(scanner, BUILTINS.copy())
    definitions = parser.program()
    # print(definitions['main'])
    s = interpret(definitions, [], definitions['main'])
    print(s)
