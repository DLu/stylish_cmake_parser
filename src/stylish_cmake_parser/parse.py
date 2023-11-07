import argparse
import pathlib
from stylish_cmake_parser import parse_file


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('path', type=pathlib.Path)
    args = parser.parse_args(argv)

    parse_file(args.path, debug=True)
