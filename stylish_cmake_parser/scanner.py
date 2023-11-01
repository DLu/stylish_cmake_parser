import collections
from enum import IntEnum
import re


Token = collections.namedtuple('Token', ['type', 'value'])

TokenType = IntEnum('TokenType', ['word', 'caps', 'string_literal', 'left_paren',
                    'right_paren', 'whitespace', 'newline', 'comment'])

ALL_CAPS = re.compile('^[A-Z_]+$')
WhiteSpaceTokens = [TokenType.whitespace, TokenType.newline]


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


def scan_cmake_tokens(s):
    tokens, remainder = CMakeScanner.scan(s)
    assert not remainder
    return tokens


def compare_token_streams(s0, s1):
    tokens0 = scan_cmake_tokens(s0)
    tokens1 = scan_cmake_tokens(s1)

    while tokens0 and tokens1:
        if tokens0[0].type in WhiteSpaceTokens:
            tokens0.pop(0)
        elif tokens1[0].type in WhiteSpaceTokens:
            tokens1.pop(0)
        else:
            token0 = tokens0.pop(0)
            token1 = tokens1.pop(0)
            assert token0.value == token1.value, f'{token0} {token1}'

    while tokens1 and tokens1[0].type in WhiteSpaceTokens:
        tokens1.pop(0)

    assert not tokens0
    assert not tokens1, tokens1
