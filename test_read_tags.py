#!/usr/bin/python3

import argparse
import base64
import json
import logging
import os
import struct
import sys

import discid

from mutagen.easyid3 import EasyID3, ID3

import struct
import discid
from mutagen.mp3 import MP3


def calc(mcdi_data):
    total_bytes = len(mcdi_data)

    # 1. Isolate the payload bytes
    remainder = total_bytes % 4
    offsets_bytes = mcdi_data[remainder:] if remainder > 0 else mcdi_data

    # 2. Extract track list count
    total_entries = len(offsets_bytes) // 4
    track_count = total_entries - 1

    # 3. Unpack raw integer numbers
    raw_offsets = list(struct.unpack(f'>{total_entries}I', offsets_bytes))

    # 4. Standard CD Lead-in Adjustment (Crucial Fix)
    # The MusicBrainz library requires adding 150 sectors (2 seconds)
    # to every single offset if your data starts at index zero.
    adjusted_offsets = [val + 150 for val in raw_offsets]

    first_track = 1
    last_track = track_count

    # Extract the corrected variables
    lead_out_sector = adjusted_offsets[-1]
    track_offsets = adjusted_offsets[:-1]

    # Double Check Constraint:
    # If the ripper somehow flipped or dropped the layout bounds,
    # ensure the lead-out sector is at least higher than the last track's start
    if lead_out_sector <= track_offsets[-1]:
        # Inject an arbitrary 150-sector standard spacing cushion
        lead_out_sector = track_offsets[-1] + 150

    # 5. Calculate and return the ID string
    disc = discid.put(first_track, last_track, lead_out_sector, track_offsets)
    return disc.id


# Example Usage:
# print("MusicBrainz Disc ID:", calculate_discid_from_mcdi("your_song.mp3"))


def collect_file_attrs(path):
    dirs = os.walk(path)
    file_attrs = {}
    count = 0
    limit = 3
    for (dirpath, dirnames, filenames) in dirs:
        files = filenames
        for file in files:
            if count >= limit:
                break

            path = os.path.join(dirpath, file)
            logging.info(path)
            file_info = os.lstat(path)
            file_attrs[path] = {
                "mode": file_info.st_mode,
                "ctime": file_info.st_ctime,
                "mtime": file_info.st_mtime,
                "atime": file_info.st_atime,
                "uid": file_info.st_uid,
                "gid": file_info.st_gid,
            }

            if not path.endswith(".mp3"):
                continue

            # Load the file
            tags = EasyID3(path)

            # View all available tag names
            logging.info("EasyId3 = %s", tags.keys())

            # Load the raw ID3 tags
            audio = ID3(path)

            # Print all available frames and their values
            for k, v in audio.items():
                logging.info("%s = '%s'", k, v)
                if k == "MCDI":
                    logging.info("** MCDI = %s", calc(v.data))

            count += 1

        if count >= limit:
            break


def main(argv):

    parser = argparse.ArgumentParser()
    parser.add_argument('directory')
    args = parser.parse_args(argv)

    collect_file_attrs(args.directory)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main(sys.argv[1:])
