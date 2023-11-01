import pathlib
from .command_sequence import CommandSequence
from .parser import CMakeParser, CMakeParseException

__all__ = ['CMakeParseException']


def parse_commands(s, debug=False):
    parser = CMakeParser(s, debug=debug)
    return parser.contents


def parse_command(s, debug=False):
    parser = CMakeParser(s, debug=debug)
    assert len(parser.contents) == 1
    return parser.contents[0]


def parse_file(filename, debug=False):
    if not isinstance(filename, pathlib.Path):
        filename = pathlib.Path(filename)
    if not filename.exists():
        return

    with open(filename) as f:
        s = f.read()
    return CommandSequence(parse_commands(s, debug))
