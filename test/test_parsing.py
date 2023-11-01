import pytest
import pathlib
import tempfile
from stylish_cmake_parser import parse_file
from stylish_cmake_parser.command import Command

DATA_FOLDER = pathlib.Path(__file__).parent / 'data'
TEST_FILES = sorted(DATA_FOLDER.iterdir())
TEST_IDS = [p.name for p in TEST_FILES]


@pytest.mark.parametrize('filepath', TEST_FILES, ids=TEST_IDS)
def test_parsing(filepath):
    assert parse_file(filepath)


def write_to_temp_and_compare(result, original):
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp:
        temp.write(str(result))
    regenerated = open(temp.name).read()
    temp.close()
    assert original == regenerated


@pytest.mark.parametrize('filepath', TEST_FILES, ids=TEST_IDS)
def test_writing(filepath):
    result = parse_file(filepath)
    original = open(filepath).read()

    write_to_temp_and_compare(result, original)

    Command.FORCE_REGENERATION = True
    write_to_temp_and_compare(result, original)
    Command.FORCE_REGENERATION = False
