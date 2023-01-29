#!/usr/bin/env python

from sys import argv, stderr

from converter import convert_file


def main(filename):
    html, messages = convert_file(filename)
    for message in messages:
        print(f"{message.type}: {message.message}", file=stderr)
    print(html)


if __name__ == "__main__":
    main(*argv[1:])
