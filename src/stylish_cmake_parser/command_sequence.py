from .command import Command
from .command_group import CommandGroup
import collections
import re

VARIABLE_PATTERN = re.compile(r'(\$\{([^\}]+)\})')  # Matches ${...}


class CommandSequence:
    def __init__(self, initial_contents=None, depth=0, parent=None):
        self.contents = []
        self.content_map = collections.defaultdict(list)
        self.depth = depth
        self.parent = parent

        if initial_contents:
            for content in initial_contents:
                self.add(content)

    def add(self, content):
        self.insert(content, smart_whitespace=False)

    def insert(self, content, index=None, smart_whitespace=True):
        if index is None:
            # If no index, insert at end
            index = len(self.contents)

        before = self.contents[:index]
        after = self.contents[index:]

        to_insert = []
        if isinstance(content, str) or not smart_whitespace:
            to_insert.append(content)
        else:
            # Insert newline if there's a command immediately before
            if before and not isinstance(before[-1], str):
                to_insert.append('\n')

            # Insert tabs if nonzero depth
            if self.depth:
                if not self.contents:
                    to_insert.append('\n')
                to_insert.append('  ' * self.depth)
                to_insert.append(content)
            else:
                to_insert.append(content)

            if not after:
                to_insert.append('\n')

        self.contents = before + to_insert + after

        if isinstance(content, Command):
            self.content_map[content.command_name].append(content)

        elif isinstance(content, CommandGroup):
            self.content_map['group'].append(content)

    def get_variables(self):
        variables = {}
        if self.parent:
            variables.update(self.parent.get_variables())

        for content in self.content_map['set']:
            tokens = content.get_tokens(include_name=True)
            variables[tokens[0]] = ' '.join(tokens[1:])
        for content in self.content_map['project']:
            variables['PROJECT_NAME'] = content.first_token()
        return variables

    def resolve_variables(self, var, error_on_missing=True):
        if isinstance(var, str):
            s = var
            variables = self.get_variables()

            m = VARIABLE_PATTERN.search(s)
            while m:
                full_string, variable_name = m.groups()
                if variable_name not in variables:
                    if error_on_missing:
                        raise KeyError(f'Variable {variable_name} not defined!')
                    else:
                        replacement = ''
                else:
                    replacement = variables[variable_name]
                s = s.replace(full_string, replacement)
                m = VARIABLE_PATTERN.search(s)
            return s
        else:
            tokens = []
            for token in var:
                # TODO: Sometimes we want to skip comments
                tokens.append(self.resolve_variables(token))
                # TODO: Sometimes resolved tokens need reparsing
                # TODO: Sometimes we want to remove the quotes from the resolutions
            return tokens

    def get_resolved_tokens(self, cmd, include_name=False):
        return self.resolve_variables(cmd.get_tokens(include_name))

    def remove_command(self, cmd):
        index = self.contents.index(cmd)

        # Remove indentation before command
        if self.depth and index > 0 and str(self.contents[index - 1]).endswith('  '):
            self.contents[index - 1] = self.contents[index - 1][:-2]

        # Remove newline after command
        if index < len(self.contents) - 1 and str(self.contents[index + 1]).startswith('\n'):
            self.contents[index + 1] = self.contents[index + 1][1:]

        del self.contents[index]
        self.content_map[cmd.command_name].remove(cmd)

    def remove_commands(self, cmd_name, recurse=True):
        for cmd in list(self.content_map[cmd_name]):
            self.remove_command(cmd)

        if recurse:
            for group in self.content_map['group']:
                group.contents.remove_commands(cmd_name, recurse)

    def __iter__(self):
        yield from self.contents

    def __repr__(self):
        return ''.join(map(str, self))
