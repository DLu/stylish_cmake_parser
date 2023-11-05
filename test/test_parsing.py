import pytest
import pathlib
import tempfile
from stylish_cmake_parser import parse_file, parse_command, Command
from stylish_cmake_parser.scanner import compare_token_streams

DATA_FOLDER = pathlib.Path(__file__).parent / 'data'
TEST_FILES = sorted(DATA_FOLDER.iterdir())
TEST_IDS = [p.name for p in TEST_FILES]


@pytest.mark.parametrize('filepath', TEST_FILES, ids=TEST_IDS)
def test_parsing(filepath):
    assert parse_file(filepath)


def test_parsing_edge_cases():
    assert parse_file('fake_file') is None


def test_single_command():
    cmd = parse_command('find_package(ament_cmake REQUIRED)')
    section0 = cmd.get_section('')
    assert section0.is_valid()
    assert len(section0.values) == 1
    assert section0.values[0] == 'ament_cmake'
    assert str(section0.style) == "SectionStyle('', ' ', ' ')"

    assert cmd.first_token() == 'ament_cmake'
    tokens = cmd.get_tokens(include_name=True)
    assert tokens == ['ament_cmake', 'REQUIRED']


def write_to_temp_and_compare(result, original):
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp:
        temp.write(str(result))
    regenerated = open(temp.name).read()
    temp.close()
    compare_token_streams(original, regenerated)


@pytest.mark.parametrize('filepath', TEST_FILES, ids=TEST_IDS)
def test_writing(filepath):
    result = parse_file(filepath)
    original = open(filepath).read()

    write_to_temp_and_compare(result, original)

    Command.FORCE_REGENERATION = True
    write_to_temp_and_compare(result, original)
    Command.FORCE_REGENERATION = False
