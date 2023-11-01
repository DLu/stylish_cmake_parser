from stylish_cmake_parser import Command, CommandSequence, Section, SectionStyle, parse_command

INSTALL_COMMAND1 = ('install(FILES data/a data/x data/y data/z data/b data/d data/e '
                    'DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}/data)')
INSTALL_COMMAND2 = 'install(DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}/data)'
INSTALL_COMMAND3 = 'install()'
INSTALL_COMMAND4 = """install(
    FILES
      data/a
      data/x
      data/y
      data/z
      data/b
      data/d
      data/e
    DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}/data
)"""


def test_simple_construction():
    cmd = Command('install')
    cmd.add_section('FILES')
    cmd.add(Section('DESTINATION'))
    cmd.add_token('${CATKIN_PACKAGE_SHARE_DESTINATION}/data')

    sections = cmd.get_sections('FILES')
    for section in sections:
        section.add('data/a')

        section.add_values(['data/y', 'data/x', 'data/z'])

        section.add('data/b')
        section.add_values(['data/d', 'data/e'])

    assert str(cmd) == INSTALL_COMMAND1

    cmd.remove_sections('FILES')
    assert str(cmd) == INSTALL_COMMAND2

    cmd.remove_sections('missing_section_says_what')
    assert str(cmd) == INSTALL_COMMAND2

    cmd.add('\n')
    cmd.remove_sections('DESTINATION')
    assert str(cmd) == INSTALL_COMMAND3


def test_raw_construction():
    cmd = Command('project')
    cmd.add_token('basic')
    seq = CommandSequence([cmd])
    assert str(seq) == 'project(basic)'


def test_styling():
    cmd = parse_command(INSTALL_COMMAND1)
    section = cmd.get_section('FILES')
    section.style = SectionStyle('\n    ', '\n      ', '\n      ')
    section = cmd.get_section('DESTINATION')
    section.style.prename = '\n    '
    cmd.changed = True
    assert str(cmd) == INSTALL_COMMAND4
