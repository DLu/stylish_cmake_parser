import pytest
import pathlib
import tempfile
from stylish_cmake_parser import parse_file

DATA_FOLDER = pathlib.Path(__file__).parent / 'data'
TEST_FILES = sorted(DATA_FOLDER.iterdir())
TEST_IDS = [p.name for p in TEST_FILES]


@pytest.mark.parametrize('filepath', TEST_FILES, ids=TEST_IDS)
def test_parsing(filepath):
    assert parse_file(filepath)


@pytest.mark.parametrize('filepath', TEST_FILES, ids=TEST_IDS)
def test_writing(filepath):
    result = parse_file(filepath)
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp:
        temp.write(str(result))

    original = open(filepath).read()
    regenerated = open(temp.name).read()

    assert original == regenerated

    temp.close()
