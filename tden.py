#!/usr/bin/python3

import argparse
import collections
import datetime
import logging
import os
import sys

from mutagen.id3 import ID3, TDEN, TXXX, Frame, Encoding


def collect_file_attrs(path):
    counts = collections.Counter()
    count = 0
    limit = None

    dirs = os.walk(path)

    for (dirpath, dirnames, filenames) in dirs:
        files = filenames
        for file in files:
            if limit is not None and count >= limit:
                break

            path = os.path.join(dirpath, file)
            logging.info(path)
            file_info = os.lstat(path)
            modified = datetime.datetime.fromtimestamp(file_info.st_mtime, tz=datetime.timezone.utc)

            if not path.endswith(".mp3"):
                continue

            counts['total_mp3s'] += 1
            # Load the raw ID3 tags
            logging.info("loading file %s", path)
            try:
                audio = ID3(path, v2_version=4)
                logging.debug("audio = %s (%s)", audio, type(audio))
                logging.info("version=%s", audio.version)

                tden = audio.getall('TDEN')
                logging.debug("tden = %s %s", type(tden), tden)

                if len(tden) == 0:
                    # Add or update the TDEN tag
                    audio.add(TDEN(text=[modified.isoformat()]))
                    #new_txxx = TXXX(encoding=3, desc="YOUR_DESCRIPTION", text="Your Value")
                    #audio.add(new_txxx)
                    audio.add(TXXX(encoding=Encoding.LATIN1, desc="original_mtime", text=modified.isoformat()))
                    audio.save(v2_version=4)

                    # 3. Apply the times as a tuple: (atime, mtime)
                    os.utime(path, times=(file_info.st_atime, file_info.st_mtime))

                    count += 1
                else:
                    counts['already'] += 1
            except Exception as exc:
                counts['error'] += 1
                logging.error("trouble processing %s: %s", path, exc, exc_info=exc)

        if limit is not None and count >= limit:
            break

    counts['processed'] = count
    logging.info("Processing counts: %s", counts)


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('directory')
    args = parser.parse_args(argv)

    collect_file_attrs(args.directory)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main(sys.argv[1:])
