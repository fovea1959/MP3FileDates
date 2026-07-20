#!/usr/bin/python3

import argparse
import datetime
import json
import logging
import os
import sys

from mutagen.id3 import ID3, TDEN, Frame


# 1. Subclass Frame for your custom type (e.g., "XMYF")
class XMTM(Frame):
    FrameID = "XMTM"

    def __init__(self, encoding=3, text=b''):
        super().__init__()
        self.encoding = encoding
        self.text = text

    # Define how your frame writes to bytes
    def _writeData(self, *args):
        # Frame flags + byte data
        data = bytes([self.encoding]) + self.text
        return data

    # Define how your frame parses from bytes (Optional but recommended)
    @classmethod
    def _fromData(cls, header, frames, options):
        encoding = frames[0]
        text = frames[1:]
        return cls(encoding=encoding, text=text)


def collect_file_attrs(path):
    with open('.saved-file-attrs', 'rb') as f:
        j = json.load(f)

    dirs = os.walk(path)
    count = 0
    limit = 10
    for (dirpath, dirnames, filenames) in dirs:
        files = filenames
        for file in files:
            if count >= limit:
                break

            path = os.path.join(dirpath, file)
            logging.info(path)

            j1 = j[path]

            file_info = os.lstat(path)
            modified = datetime.datetime.fromtimestamp(file_info.st_mtime, tz=datetime.timezone.utc)

            if not path.endswith(".mp3"):
                continue

            # Load the raw ID3 tags
            audio = ID3(path, known_frames={"XMTM": XMTM})
            logging.info("audio = %s (%s)", audio, type(audio))

            tden = audio.getall('TDEN')
            logging.info("tden = %s %s", type(tden), tden)

            if False and len(tden) == 0:
                # Add or update the TDEN tag
                audio.add(TDEN(text=[modified.isoformat()]))
                audio.add(XMTM(text=modified.isoformat().encode()))
                audio.save()

                # 3. Apply the times as a tuple: (atime, mtime)
                os.utime(path, times=(file_info.st_atime, file_info.st_mtime))

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
