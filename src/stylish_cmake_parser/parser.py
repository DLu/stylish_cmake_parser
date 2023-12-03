from .command_group import CommandGroup
from .command_sequence import CommandSequence
from .command import Command
from .scanner import scan_cmake_tokens, TokenType, WhiteSpaceTokens
from .section import Section, SectionStyle

import sys
import collections

NOT_REAL = WhiteSpaceTokens + [TokenType.comment]


class CMakeParseException(Exception):
    pass


def match_command_groups(contents, base_depth=0, parent=None):
    revised_seq = CommandSequence(depth=base_depth, parent=parent)

    current = []
    group = None
    depth = base_depth

    for content in contents:
        if group is None:
            if isinstance(content, Command) and content.command_name.lower() in ['if', 'foreach']:
                group = content
                depth = base_depth + 1
            else:
                revised_seq.append(content)
        else:
            if isinstance(content, Command):
                if content.command_name.lower() == group.command_name.lower():
                    depth += 1
                elif content.command_name.lower() == 'end' + group.command_name.lower():
                    depth -= 1
                    if depth == base_depth:
                        recursive_seq = match_command_groups(current, base_depth + 1, revised_seq)
                        cg = CommandGroup(group, recursive_seq, content)
                        revised_seq.append(cg)
                        group = None
                        current = []
                        continue
            current.append(content)

    if depth != base_depth:
        raise CMakeParseException(f'Unmatched {group.command_name} tag')

    return revised_seq


class CMakeParser:
    def __init__(self, s, debug=False):
        self.seq = CommandSequence()

        self.tokens = scan_cmake_tokens(s)

        if debug:
            for token in self.tokens:
                print(f'[{token.type.name:>11}]{repr(token.value)}')

        try:
            while self.tokens:
                token_type = self.get_type()
                if token_type == TokenType.comment:
                    self.seq.append(self.match(token_type))
                elif token_type == TokenType.newline or token_type == TokenType.whitespace:
                    s = self.match(token_type)
                    self.seq.append(s)
                elif token_type in [TokenType.word, TokenType.caps]:
                    cmd = self.parse_command()
                    self.seq.append(cmd)
                else:
                    raise CMakeParseException(f'Unexpected token of type {token_type.name}')

            # Match Command Groups
            self.seq = match_command_groups(self.seq.contents, self.seq.depth)
        except Exception:
            if self.tokens:
                token = self.tokens[0]
                ind = token.start_index
                sys.stderr.write(f'Error on Line {ind.line_no}, Char {ind.char_no}\n')
            raise

        if debug:
            for chunk in self.seq:
                print(f'[{chunk}]')

    def get_type(self):
        if self.tokens:
            return self.tokens[0].type

    def next_real_type(self):
        for token in self.tokens:
            if token.type not in NOT_REAL:
                return token.type

    def match(self, token_type=None):
        if not self.tokens:
            if token_type is None:
                raise CMakeParseException('Attempt to match any token but none left!')
            else:
                raise CMakeParseException(f'Attempt to match {token_type.name} token but none left!')
        if token_type is None or self.get_type() == token_type:
            token = self.tokens.pop(0)
            return token.value
        else:
            raise CMakeParseException(f'Expected type "{token_type.name}" but got "{self.get_type()}"')

    def parse_command(self):
        command_name = self.match()
        original = command_name
        cmd = Command(command_name, parent=self.seq)
        while self.get_type() in WhiteSpaceTokens:
            s = self.match()
            cmd.pre_paren += s
            original += s
        original += self.match(TokenType.left_paren)
        paren_depth = 1

        while self.tokens:
            token_type = self.next_real_type()
            if token_type in [TokenType.word, TokenType.caps, TokenType.string_literal]:
                section, s = self.parse_section(cmd)
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
                    else:
                        cmd.add_token(token.value)
                elif token.type == TokenType.left_paren:
                    cmd.add_token(token.value)
                    paren_depth += 1
                else:
                    cmd.sections.append(token.value)
        raise CMakeParseException(f'File ended while processing command "{command_name}"')

    def parse_section(self, parent):
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
            while self.get_type() in WhiteSpaceTokens:
                s = self.match()
                original += s
                style.name_val_sep += s
            if len(style.name_val_sep) == 0:
                style.name_val_sep = ' '

        delim_counts = collections.Counter()
        current = ''
        while self.next_real_type() not in [TokenType.left_paren, TokenType.right_paren, TokenType.caps]:
            token_type = self.get_type()
            if token_type in WhiteSpaceTokens:
                token = self.match()
                original += token
                current += token
            else:
                if len(current) > 0:
                    delim_counts[current] += 1
                current = ''
                token = self.match()
                original += token
                tokens.append(token)
        assert not current  # Current should be empty
        if delim_counts:
            top_n = delim_counts.most_common(1)  # Where n = 1
            style.val_sep = top_n[0][0]  # Get actual delim from first token

        return Section(cat, tokens, style, parent), original
