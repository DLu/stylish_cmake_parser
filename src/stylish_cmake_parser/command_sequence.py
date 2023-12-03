from .command import Command
from .command_group import CommandGroup
from .element import CMakeElement
import collections
from enum import IntEnum
import re

VARIABLE_PATTERN = re.compile(r'(\$\{([^\}]+)\})')  # Matches ${...}


class MissingVariableResult(IntEnum):
    ERROR = 1
    ORIGINAL = 2
    EMPTY = 3


class CommandSequence(CMakeElement):
    def __init__(self, initial_contents=None, depth=0, parent=None):
        super().__init__(parent)
        self.contents = []
        self.content_map = collections.defaultdict(list)
        self.depth = depth

        if initial_contents:
            for content in initial_contents:
                self.append(content)

    def add(self, content):
        self.insert(content, smart_whitespace=False)

    def append(self, content):
        """Insert at end without any fanciness or marking changes"""
        self.contents.append(content)
        self.update_references(content)

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
        self.update_references(content)

        self.mark_changed()

    def update_references(self, content):
        if isinstance(content, Command):
            self.content_map[content.command_name].append(content)
            content.parent = self

        elif isinstance(content, CommandGroup):
            self.content_map['group'].append(content)
            content.parent = self

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

    def resolve_variables(self, var, missing_result=MissingVariableResult.ORIGINAL):
        if isinstance(var, str):
            prefix = ''
            s = var
            variables = self.get_variables()

            m = VARIABLE_PATTERN.search(s)
            while m:
                full_string, variable_name = m.groups()
                if variable_name not in variables:
                    if missing_result == MissingVariableResult.ERROR:
                        raise KeyError(f'Variable {variable_name} not defined!')
                    elif missing_result == MissingVariableResult.EMPTY:
                        replacement = ''
                    else:
                        index = s.index(full_string)
                        prefix = s[:index + 1]
                        s = s[index + 1:]
                        replacement = full_string
                else:
                    replacement = variables[variable_name]
                s = s.replace(full_string, replacement)
                m = VARIABLE_PATTERN.search(s)
            return prefix + s
        else:
            tokens = []
            for token in var:
                # TODO: Sometimes we want to skip comments
                tokens.append(self.resolve_variables(token, missing_result))
                # TODO: Sometimes resolved tokens need reparsing
                # TODO: Sometimes we want to remove the quotes from the resolutions
            return tokens

    def get_resolved_tokens(self, cmd, include_name=False):
        return self.resolve_variables(cmd.get_tokens(include_name))

    def get_build_rules(self, tag, resolve_target_name=False):
        rules = {}
        for cmd in self.content_map[tag]:
            resolved_tokens = self.get_resolved_tokens(cmd, True)

            if resolve_target_name:
                target = resolved_tokens[0]
            else:
                tokens = cmd.get_tokens(True)
                target = tokens[0]

            deps = resolved_tokens[1:]
            rules[target] = deps
        return rules

    def get_source_files_by_build_rule(self, tag):
        sources = set()
        for deps in self.get_build_rules(tag).values():
            sources.update(deps)
        return sources

    def get_library_source(self):
        return self.get_source_files_by_build_rule('add_library')

    def get_executable_source(self):
        return self.get_source_files_by_build_rule('add_executable')

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
        self.mark_changed()

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
