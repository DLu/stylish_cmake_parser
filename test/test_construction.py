from stylish_cmake_parser import Command, CommandGroup, CommandSequence, Section, SectionStyle, parse_command

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
    cmd.add(Section('DESTINATION', parent=cmd))
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


def test_multiple_commands():
    cmd0 = Command('project')
    cmd0.add_token('xyz')
    cmd1 = Command('cmake_minimum_required')
    cmd1.add_token('VERSION')
    cmd1.add_token('3.0.2')

    cs0 = CommandSequence()
    cs0.add(cmd0)
    cs0.add(cmd1)
    assert str(cs0) == 'project(xyz)cmake_minimum_required(VERSION 3.0.2)'

    cs1 = CommandSequence()
    cs1.insert(cmd0)
    cs1.insert(cmd1)
    assert str(cs1) == 'project(xyz)\ncmake_minimum_required(VERSION 3.0.2)\n'

    cmd2 = Command('catkin_python_setup')
    cs1.insert(cmd2, 1)
    assert str(cs1) == 'project(xyz)\ncatkin_python_setup()\ncmake_minimum_required(VERSION 3.0.2)\n'

    cs2 = CommandSequence()
    cs2.insert(cmd0)

    start = Command('if')
    start.add_token('TESTING')
    end = Command('endif')
    inner = CommandSequence(depth=1)
    cmd3 = Command('find_package')
    cmd3.add_token('rostest')
    inner.insert(cmd3)
    cmd4 = Command('find_package')
    cmd4.add_token('roslint')
    inner.insert(cmd4)
    cg = CommandGroup(start, inner, end)
    cs2.insert(cg)

    assert str(cs2) == """project(xyz)
if(TESTING)
  find_package(rostest)
  find_package(roslint)
endif()
"""


def test_styling():
    cmd = parse_command(INSTALL_COMMAND1)
    section = cmd.get_section('FILES')
    section.style = SectionStyle('\n    ', '\n      ', '\n      ')
    section = cmd.get_section('DESTINATION')
    section.style.prename = '\n    '
    section.mark_changed()
    assert str(cmd) == INSTALL_COMMAND4
