#!/usr/bin/python3

import argparse
import logging
import os
import pathlib
import sys

from mutagen.id3 import ID3


def collect_file_attrs(path_s):
    root_path = pathlib.Path(path_s)
    file_attrs = []
    for (dirpath_s, _, filenames) in root_path.walk():
        dirpath = pathlib.Path(dirpath_s)
        for filename in filenames:
            if not filename.endswith(".mp3"):
                continue

            path = dirpath / pathlib.Path(filename)
            fa = {
                "path": path,
                "relpath": path.relative_to(root_path),
            }

            # Load the raw ID3 tags
            audio = ID3(path)

            # Print all available frames and their values
            tden = audio.getall('TDEN')
            if len(tden) == 1:
                #logging.info("TDEN = %s", tden)
                fa['tden'] = tden[0].text[0]
                file_attrs.append(fa)
            elif len(tden) > 2:
                raise ValueError(f"{path} has too much TDEN: {tden}")
            else:
                pass

            logging.debug(fa)

    file_attrs.sort(key=lambda fa: (fa['tden'], fa['relpath']), reverse=True)

    return file_attrs


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('directory')
    parser.add_argument('--verbose', action='store_true')
    parser.add_argument('--output', required=True)
    args = parser.parse_args(argv)

    if args.verbose:
        logging.getLogger('').setLevel(logging.DEBUG)

    file_attrs = collect_file_attrs(args.directory)
    with open(args.output, 'w') as f:
        for fa in file_attrs:
            print(f"# {fa['tden']}", file=f)
            print(fa['relpath'], file=f)



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main(sys.argv[1:])
