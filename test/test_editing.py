from stylish_cmake_parser import parse_file
import pathlib
import tempfile

EXPECTED_RESULT = """cmake_minimum_required(VERSION 3.0.2)
project(roscompile)


catkin_python_setup()

catkin_package(
    CATKIN_DEPENDS catkin ros_introspection
)

if(CATKIN_ENABLE_TESTING)
  set(ROSLINT_PYTHON_OPTS --max-line-length=120 --ignore=E111,E114,E302)

  catkin_download_test_data(test_data.zip
      https://github.com/DLu/roscompile_test_data/raw/main/test_data.zip
      DESTINATION ${CATKIN_DEVEL_PREFIX}/${CATKIN_PACKAGE_SHARE_DESTINATION}/test
  )

  catkin_add_nosetests(test/utest.py)
  roslint_python()
  roslint_add_test()
endif()

catkin_install_python(PROGRAMS
                      scripts/roscompile
                      scripts/add_tests
                      scripts/convert_to_format_2
                      scripts/add_compile_options
                      scripts/roscompile_command
                      scripts/upgrade_manifest
                      scripts/noetic_migration
                      DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)
install(FILES data/cmake.ignore data/cmake_patterns.ignore data/package.ignore data/package_patterns.ignore
        DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}/data
)
"""


def test_command_removal():
    cmake = parse_file(pathlib.Path(__file__).parent / 'data' / 'roscompile.txt')

    cmake.remove_commands('find_package')

    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp:
        temp.write(str(cmake))
    regenerated = open(temp.name).read()
    temp.close()

    assert regenerated == EXPECTED_RESULT
