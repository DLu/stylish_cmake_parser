import collections
from enum import IntEnum
import re

TextIndex = collections.namedtuple('TextIndex', ['line_no', 'char_no'])
Token = collections.namedtuple('Token', ['type', 'value', 'start_index', 'end_index'])

TokenType = IntEnum('TokenType', ['word', 'caps', 'string_literal', 'left_paren',
                    'right_paren', 'whitespace', 'newline', 'comment'])

ALL_CAPS = re.compile('^[A-Z_]+$')
WhiteSpaceTokens = [TokenType.whitespace, TokenType.newline]
text_index = None

# As a hack to avoid making the grammar more complex,
# we replace \" (backslash quote) with 𝄥 (Musical symbol drum clef-1)
# and then convert it back after scanning
BACKSLASH_QUOTE = '\\"'
QUOTE_REPLACEMENT = '𝄥'


def make_token(scanner, token, token_type):
    global text_index
    start_index = text_index
    token = token.replace(QUOTE_REPLACEMENT, BACKSLASH_QUOTE)
    if '\n' in token:
        nl_i = token.rindex('\n')
        text_index = TextIndex(text_index.line_no + 1, 1 + len(token) - nl_i - 1)
    else:
        text_index = TextIndex(text_index.line_no, text_index.char_no + len(token))

    return Token(token_type, token, start_index, text_index)


CMakeScanner = re.Scanner([
    (r'#.*\n', lambda scanner, token: make_token(scanner, token, TokenType.comment)),
    (r'"[^"]*"', lambda scanner, token: make_token(scanner, token, TokenType.string_literal)),
    (r'\(', lambda scanner, token: make_token(scanner, token, TokenType.left_paren)),
    (r'\)', lambda scanner, token: make_token(scanner, token, TokenType.right_paren)),
    (r'[^ \t\r\n()#"]+', lambda scanner, token: make_token(scanner,
     token, TokenType.caps if ALL_CAPS.match(token) else TokenType.word)),
    (r'\n', lambda scanner, token: make_token(scanner, token, TokenType.newline)),
    (r'[ \t]+', lambda scanner, token: make_token(scanner, token, TokenType.whitespace)),
])


def scan_cmake_tokens(s):
    global text_index
    text_index = TextIndex(1, 1)
    assert QUOTE_REPLACEMENT not in s
    s = s.replace(BACKSLASH_QUOTE, QUOTE_REPLACEMENT)
    tokens, remainder = CMakeScanner.scan(s)
    if remainder and remainder[0] == '#' and '\n' not in remainder:
        tokens.append(Token(TokenType.comment, remainder, None, None))
        remainder = ''
    assert not remainder, remainder
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
