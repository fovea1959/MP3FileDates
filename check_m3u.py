#!/usr/bin/python3

import argparse
import collections
import logging
import pathlib
import sys


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('m3u')
    parser.add_argument('--remove-prefix')
    parser.add_argument('--relative-to')
    parser.add_argument('--verbose', action='store_true')
    args = parser.parse_args(argv)

    if args.verbose:
        logging.getLogger('').setLevel(logging.DEBUG)

    prefix = None
    if args.remove_prefix is not None:
        prefix = pathlib.Path(args.remove_prefix)

    relative_to = None
    if args.relative_to is not None:
        relative_to = pathlib.Path(args.relative_to)

    c = collections.Counter()

    with open(args.m3u, 'r') as f:
        for i, line in enumerate(f):
            line = line.strip()
            if line.startswith('#'):
                continue

            filepath = pathlib.Path(line)
            if prefix is not None:
                filepath = filepath.relative_to(prefix)
            if relative_to is not None:
                filepath = relative_to / filepath

            if not filepath.exists():
                logging.error("%d: file %s is missing", i+1, filepath)
                c['missing'] += 1
            elif not filepath.is_file():
                logging.error("%d: file %s is not a file", i+1, filepath)
                c['not a file'] += 1
            else:
                c['ok'] += 1

    logging.info("done: %s", c)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main(sys.argv[1:])
