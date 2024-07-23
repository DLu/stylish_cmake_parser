import pytest
import pathlib
from stylish_cmake_parser import parse_file, CMakeParseException

DATA_FOLDER = pathlib.Path(__file__).parent / 'bad_data'


def test_leftover():
    with pytest.raises(CMakeParseException) as e_info:
        parse_file(DATA_FOLDER / 'leftover.txt')
    assert 'Expected type "left_paren"' in str(e_info.value)
    assert 'leftover.txt' in str(e_info.value)
    assert e_info.value.line_no == 3
    assert e_info.value.char_no == 1


def test_unexpected():
    with pytest.raises(CMakeParseException) as e_info:
        parse_file(DATA_FOLDER / 'unexpected.txt')
    assert 'Unexpected token of type left_paren' in str(e_info.value)
    assert 'unexpected.txt' in str(e_info.value)
    assert e_info.value.line_no == 1
    assert e_info.value.char_no == 1


def test_unresolved():
    with pytest.raises(CMakeParseException) as e_info:
        parse_file(DATA_FOLDER / 'unresolved.txt')
    assert 'Attempt to match any token but none left!' in str(e_info.value)
    assert 'unresolved.txt' in str(e_info.value)
    assert e_info.value.line_no == 2
    assert e_info.value.char_no == 1


def test_unbalanced():
    with pytest.raises(CMakeParseException) as e_info:
        parse_file(DATA_FOLDER / 'unbalanced.txt')
    assert 'File ended while processing command' in str(e_info.value)
    assert 'unbalanced.txt' in str(e_info.value)
    assert e_info.value.line_no == 2
    assert e_info.value.char_no == 1


def test_unfinished():
    with pytest.raises(CMakeParseException) as e_info:
        parse_file(DATA_FOLDER / 'unfinished.txt')
    assert 'Attempt to match left_paren token but none left!' in str(e_info.value)
    assert 'unfinished.txt' in str(e_info.value)
    assert e_info.value.line_no == 2
    assert e_info.value.char_no == 1


def test_unmatched():
    with pytest.raises(CMakeParseException) as e_info:
        parse_file(DATA_FOLDER / 'unmatched.txt')
    assert 'Unmatched if tag' in str(e_info.value)
    assert 'unmatched.txt' in str(e_info.value)
    assert e_info.value.line_no == 3
    assert e_info.value.char_no == 1
