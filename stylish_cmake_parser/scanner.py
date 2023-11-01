import collections
from enum import IntEnum
import re


Token = collections.namedtuple('Token', ['type', 'value'])

TokenType = IntEnum('TokenType', ['word', 'caps', 'string_literal', 'left_paren',
                    'right_paren', 'whitespace', 'newline', 'comment'])

ALL_CAPS = re.compile('^[A-Z_]+$')


def word_cb(scanner, token):
    if ALL_CAPS.match(token):
        return Token(TokenType.caps, token)
    else:
        return Token(TokenType.word, token)


CMakeScanner = re.Scanner([
    (r'#.*\n', lambda scanner, token: Token(TokenType.comment, token)),
    (r'"[^"]*"', lambda scanner, token: Token(TokenType.string_literal, token)),
    (r'\(', lambda scanner, token: Token(TokenType.left_paren, token)),
    (r'\)', lambda scanner, token: Token(TokenType.right_paren, token)),
    (r'[^ \t\r\n()#"]+', word_cb),
    (r'\n', lambda scanner, token: Token(TokenType.newline, token)),
    (r'[ \t]+', lambda scanner, token: Token(TokenType.whitespace, token)),
])
