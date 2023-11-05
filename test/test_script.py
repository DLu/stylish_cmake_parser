from stylish_cmake_parser.parse import main
import pathlib


def test_debug(capsys):
    EXPECTED_DEBUG = """[       word]'project'
[ left_paren]'('
[       word]'basic'
[right_paren]')'
[    newline]'\\n'
[project(basic)]
[
]
"""
    path = pathlib.Path(__file__).parent / 'data' / 'basic.txt'

    main([str(path)])
    captured = capsys.readouterr()
    assert captured.out == EXPECTED_DEBUG
