from stylish_cmake_parser import parse_file, parse_command, MissingVariableResult
from stylish_cmake_parser import Command, CommandGroup, CommandSequence
import pathlib
import pytest


def test_variables():
    cmake = parse_file(pathlib.Path(__file__).parent / 'data' / 'roscompile.txt')

    inner_bit = cmake.content_map['group'][0].contents

    command = parse_command('message(ROSLINT_PYTHON_OPTS=${ROSLINT_PYTHON_OPTS})')
    msg = inner_bit.get_resolved_tokens(command, include_name=True)
    assert msg == ['ROSLINT_PYTHON_OPTS=--max-line-length=120 --ignore=E111,E114,E302']

    command2 = cmake.contents[0]
    msg2 = cmake.get_resolved_tokens(command2, include_name=True)
    assert msg2 == ['VERSION', '3.0.2']

    command3 = parse_command('add_library(${PROJECT_NAME} src/main.cpp)')
    msg3 = cmake.get_resolved_tokens(command3, include_name=True)
    assert msg3 == ['roscompile', 'src/main.cpp']

    msg4 = inner_bit.get_resolved_tokens(command3, include_name=True)
    assert msg4 == ['roscompile', 'src/main.cpp']

    with pytest.raises(KeyError):
        cmake.resolve_variables('${FAKE_VAR}', MissingVariableResult.ERROR)

    assert cmake.resolve_variables('${FAKE_VAR}', MissingVariableResult.EMPTY) == ''
    assert cmake.resolve_variables('${FAKE_VAR}', MissingVariableResult.ORIGINAL) == '${FAKE_VAR}'


def test_recursion():
    start = Command('if')
    start.add_token('TESTING')
    end = Command('endif')
    inner = CommandSequence()
    cg = CommandGroup(start, inner, end)

    assert not cg.get_variables()
