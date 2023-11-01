import collections
from .command import Command
from .command_group import CommandGroup


class CommandSequence:
    def __init__(self, initial_contents=None, depth=0):
        if initial_contents is None:
            self.contents = []
        else:
            self.contents = initial_contents
        self.content_map = collections.defaultdict(list)
        self.depth = depth

        for content in self.contents:
            if content.__class__ == Command:
                self.content_map[content.command_name].append(content)
            elif content.__class__ == CommandGroup:
                self.content_map['group'].append(content)

    def __repr__(self):
        return ''.join(map(str, self.contents))
