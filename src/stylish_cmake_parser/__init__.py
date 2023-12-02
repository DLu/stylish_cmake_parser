import pathlib
from .command import Command
from .command_group import CommandGroup
from .command_sequence import CommandSequence, MissingVariableResult
from .parser import CMakeParser, CMakeParseException
from .section import Section, SectionStyle

__all__ = ['Command', 'CommandGroup', 'CommandSequence',
           'MissingVariableResult', 'CMakeParseException', 'Section', 'SectionStyle']


def parse_commands(s, debug=False):
    parser = CMakeParser(s, debug=debug)
    return parser.seq


def parse_command(s, debug=False):
    parser = CMakeParser(s, debug=debug)
    assert len(parser.seq.contents) == 1
    return parser.seq.contents[0]


def parse_file(filename, debug=False):
    if not isinstance(filename, pathlib.Path):
        filename = pathlib.Path(filename)
    if not filename.exists():
        return

    with open(filename) as f:
        s = f.read()
    return parse_commands(s, debug)
