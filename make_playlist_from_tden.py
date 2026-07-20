#!/usr/bin/python3

import argparse
import datetime
import logging
import os
import pathlib
import sys

from mutagen.id3 import ID3


def collect_file_attrs(path_s):
    root_path = pathlib.Path(path_s)
    data = []
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
                fa['tden'] = datetime.datetime.fromisoformat(str(tden[0].text[0]))
                data.append(fa)
            elif len(tden) > 2:
                raise ValueError(f"{path} has too much TDEN: {tden}")
            else:
                pass

            logging.debug(fa)

    data.sort(key=lambda fa: (fa['tden'], fa['relpath']))

    # Step 2: Group close items together sequentially
    threshold = datetime.timedelta(minutes=5)
    clusters = []
    current_cluster = [data[0]] if data else []

    for current_data in data[1:]:
        current_date = current_data['tden']
        preceding_date = current_cluster[-1]['tden']
        # Check if this date is close to the LAST date added to the current cluster
        if current_date - preceding_date <= threshold:
            current_cluster.append(current_data)
        else:
            clusters.append(current_cluster)
            current_cluster = [current_data]

    if current_cluster:
        clusters.append(current_cluster)

    clusters.reverse()

    rv = []

    # Print results
    for i, cluster in enumerate(clusters):
        print(f"Group {i + 1}")
        for fa in cluster:
            print(f"- {fa['tden'].isoformat()} {fa['relpath']}")
            rv.append(fa)

    return rv


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
