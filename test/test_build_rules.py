from stylish_cmake_parser import parse_file
import pathlib


def test_build_rules():
    cmake = parse_file(pathlib.Path(__file__).parent / 'data' / 'dwb_local_planner.txt')

    lib_files = cmake.get_library_source()
    assert 'src/publisher.cpp' in lib_files
    assert len(lib_files) == 6

    exec_files = cmake.get_executable_source()
    assert 'src/planner_node.cpp' in exec_files
    assert len(exec_files) == 1

    build_rules0 = cmake.get_build_rules('add_executable')
    build_rules1 = cmake.get_build_rules('add_executable', resolve_target_name=True)

    assert len(build_rules0) == 1
    assert len(build_rules1) == 1
    assert '${PROJECT_NAME}_planner_node' in build_rules0
    assert 'dwb_local_planner_planner_node' in build_rules1
