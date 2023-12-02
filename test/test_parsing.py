import pytest
import pathlib
import tempfile
from stylish_cmake_parser import parse_file, parse_command, Command, CommandSequence, CommandGroup
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


def test_first_token_cases():
    # Covered above, but just to be sure...
    cmd0 = parse_command('find_package(ament_cmake REQUIRED)')
    assert cmd0.first_token() == 'ament_cmake'

    cmd1 = parse_command('install(FILES data/cmake.ignore)')
    assert cmd1.first_token() == 'FILES'

    cmd2 = parse_command('find_package()')
    assert cmd2.first_token() == ''


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


@pytest.mark.parametrize('filepath', TEST_FILES, ids=TEST_IDS)
def test_parentage(filepath):

    def parentage_check(content, parent):
        if isinstance(content, str):
            return

        assert content.parent == parent, f'Parent of {content.__class__} not set properly'

        if isinstance(content, Command):
            for section in content.sections:
                parentage_check(section, content)
        elif isinstance(content, CommandSequence):
            for content2 in content.contents:
                parentage_check(content2, content)
        elif isinstance(content, CommandGroup):
            parentage_check(content.initial_cmd, content)
            parentage_check(content.contents, content)
            parentage_check(content.close_cmd, content)

    result = parse_file(filepath)
    parentage_check(result, None)
