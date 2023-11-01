import pytest
import pathlib
from stylish_cmake_parser import parse_file, CMakeParseException

DATA_FOLDER = pathlib.Path(__file__).parent / 'bad_data'


def test_leftover():
    with pytest.raises(CMakeParseException) as e_info:
        parse_file(DATA_FOLDER / 'leftover.txt')
    assert 'Expected type "left_paren"' in str(e_info)


def test_unexpected():
    with pytest.raises(CMakeParseException) as e_info:
        parse_file(DATA_FOLDER / 'unexpected.txt')
    assert 'Unexpected token of type left_paren' in str(e_info)


def test_unresolved():
    with pytest.raises(CMakeParseException) as e_info:
        parse_file(DATA_FOLDER / 'unresolved.txt')
    assert 'Attempt to match any token but none left!' in str(e_info)


def test_unbalanced():
    with pytest.raises(CMakeParseException) as e_info:
        parse_file(DATA_FOLDER / 'unbalanced.txt')
    assert 'File ended while processing command' in str(e_info)


def test_unfinished():
    with pytest.raises(CMakeParseException) as e_info:
        parse_file(DATA_FOLDER / 'unfinished.txt')
    assert 'Attempt to match left_paren token but none left!' in str(e_info)


def test_unmatched():
    with pytest.raises(CMakeParseException) as e_info:
        parse_file(DATA_FOLDER / 'unmatched.txt')
    assert 'Unmatched if tag' in str(e_info)
