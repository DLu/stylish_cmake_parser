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
        self.variables = {}

        if initial_contents:
            for content in initial_contents:
                self.add(content)

    def add(self, content):
        self.contents.append(content)
        if isinstance(content, Command):
            self.content_map[content.command_name].append(content)

            # Track variables
            if content.command_name == 'set':
                tokens = content.get_tokens(include_name=True)
                self.variables[tokens[0]] = ' '.join(tokens[1:])
            elif content.command_name == 'project':
                self.variables['PROJECT_NAME'] = content.first_token()

        elif isinstance(content, CommandGroup):
            self.content_map['group'].append(content)

    def get_all_variables(self):
        all_vars = {}
        if self.parent:
            all_vars.update(self.parent.get_all_variables())
        all_vars.update(self.variables)
        return all_vars

    def resolve_variables(self, var, error_on_missing=True):
        if isinstance(var, str):
            s = var
            variables = self.get_all_variables()

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

    def __iter__(self):
        yield from self.contents

    def __repr__(self):
        return ''.join(map(str, self))
