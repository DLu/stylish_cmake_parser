import argparse
import pathlib
from stylish_cmake_parser import parse_file


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('path', type=pathlib.Path)
    args = parser.parse_args()

    k = parse_file(args.path, debug=True)
    print(k.contents[0].get_sections(''))


if __name__ == '__main__':
    main()
