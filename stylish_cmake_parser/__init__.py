import pathlib
from .command_sequence import CommandSequence
from .parser import CMakeParser

__all__ = []


def parse_commands(s):
    parser = CMakeParser(s)
    return parser.contents


def parse_command(s):
    parser = CMakeParser(s)
    assert len(parser.contents) == 1
    return parser.contents[0]


def parse_file(filename):
    if not isinstance(filename, pathlib.Path):
        filename = pathlib.Path(filename)
    if not filename.exists():
        return

    with open(filename) as f:
        s = f.read()
    return CommandSequence(parse_commands(s))
