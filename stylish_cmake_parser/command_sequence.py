import collections
from .command import Command
from .command_group import CommandGroup


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
        self.contents.append(content)
        if isinstance(content, Command):
            self.content_map[content.command_name].append(content)
        elif isinstance(content, CommandGroup):
            self.content_map['group'].append(content)

    def __iter__(self):
        yield from self.contents

    def __repr__(self):
        return ''.join(map(str, self))
