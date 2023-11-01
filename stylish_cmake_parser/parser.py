from .command_group import CommandGroup
from .command_sequence import CommandSequence
from .command import Command
from .scanner import CMakeScanner, TokenType
from .section import Section, SectionStyle

import sys

ALL_WHITESPACE = [TokenType.whitespace, TokenType.newline]
NOT_REAL = ALL_WHITESPACE + [TokenType.comment]


class CMakeParseException(Exception):
    pass


def match_command_groups(contents, base_depth=0):
    revised_contents = []

    current = []
    group = None
    depth = base_depth

    for content in contents:
        if group is None:
            if content.__class__ == Command and content.command_name in ['if', 'foreach']:
                group = content
                depth = base_depth + 1
            else:
                revised_contents.append(content)
        else:
            if content.__class__ == Command:
                if content.command_name == group.command_name:
                    depth += 1
                elif content.command_name == 'end' + group.command_name:
                    depth -= 1
                    if depth == base_depth:
                        recursive_contents = match_command_groups(current, base_depth + 1)
                        sub = CommandSequence(recursive_contents, depth=base_depth + 1)
                        cg = CommandGroup(group, sub, content)
                        revised_contents.append(cg)
                        group = None
                        current = []
                        continue
            current.append(content)

    # Only will happen if the tags don't match. Shouldn't happen, but resolve leftovers
    if len(current) > 0:
        revised_contents += current

    return revised_contents


class CMakeParser:
    def __init__(self, s, debug=False):
        self.contents = []

        self.tokens, remainder = CMakeScanner.scan(s)
        if remainder != '':
            raise CMakeParseException(f'Unrecognized tokens: {remainder}')

        if debug:
            for token_type, token in self.tokens:
                print(f'[{token_type}]{repr(token)}')

        while self.tokens:
            token_type = self.get_type()
            if token_type == TokenType.comment:
                self.contents.append(self.match(token_type))
            elif token_type == TokenType.newline or token_type == TokenType.whitespace:
                s = self.match(token_type)
                self.contents.append(s)
            elif token_type in [TokenType.word, TokenType.caps]:
                cmd = self.parse_command()
                self.contents.append(cmd)
            else:
                raise CMakeParseException(f'Unexpected token of type {token_type}')

        # Match Command Groups
        self.contents = match_command_groups(self.contents)

        if debug:
            for chunk in self.contents:
                print(f'[{chunk}]')

    def get_type(self):
        if self.tokens:
            return self.tokens[0].type

    def next_real_type(self):
        for token in self.tokens:
            if token.type not in NOT_REAL:
                return token.type

    def match(self, token_type=None):
        if token_type is None or self.get_type() == token_type:
            token = self.tokens.pop(0)
            return token.value
        else:
            sys.stderr.write('Token Dump:\n')
            for token in self.tokens:
                sys.stderr.write('{token}\n')
            raise CMakeParseException(f'Expected type "{token_type}" but got "{self.get_type()}"')

    def parse_command(self):
        command_name = self.match()
        original = command_name
        cmd = Command(command_name)
        while self.get_type() == TokenType.whitespace:
            s = self.match(TokenType.whitespace)
            cmd.pre_paren += s
            original += s
        original += self.match(TokenType.left_paren)
        paren_depth = 1

        while self.tokens:
            token_type = self.next_real_type()
            if token_type in [TokenType.word, TokenType.caps, TokenType.string_literal]:
                section, s = self.parse_section()
                cmd.sections.append(section)
                original += s
            else:
                token = self.tokens.pop(0)
                original += token.value
                if token.type == TokenType.right_paren:
                    paren_depth -= 1
                    if paren_depth == 0:
                        cmd.original = original
                        return cmd
                elif token.type == TokenType.left_paren:
                    paren_depth += 1
                else:
                    cmd.sections.append(token.value)
        raise CMakeParseException(f'File ended while processing command "{command_name}"')

    def parse_section(self):
        original = ''
        style = SectionStyle()
        tokens = []
        cat = ''
        while self.get_type() in NOT_REAL:
            s = self.match()
            original += s
            style.prename += s

        if self.get_type() == TokenType.caps:
            cat = self.match(TokenType.caps)
            original += cat
            style.name_val_sep = ''
            while self.get_type() in ALL_WHITESPACE:
                s = self.match()
                original += s
                style.name_val_sep += s
            if len(style.name_val_sep) == 0:
                style.name_val_sep = ' '

        delims = set()
        current = ''
        while self.next_real_type() not in [TokenType.left_paren, TokenType.right_paren, TokenType.caps]:
            token_type = self.get_type()
            if token_type in ALL_WHITESPACE:
                token = self.match()
                original += token
                current += token
            else:
                if len(current) > 0:
                    delims.add(current)
                current = ''
                token = self.match()
                original += token
                tokens.append(token)
        if len(current) > 0:
            delims.add(current)
        if len(delims) > 0:
            if len(delims) == 1:
                style.val_sep = list(delims)[0]
            else:
                # TODO: Smarter multi delim parsing
                # print(delims)
                style.val_sep = list(delims)[0]

        return Section(cat, tokens, style), original
