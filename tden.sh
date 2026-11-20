#!/bin/bash
#
find . -type f -name "*.mp3" | while read -r file; do
    # 1. Capture the file's modification time in ISO 8601 format
    mod_time=$(date -r "$file" +"%Y-%m-%dT%H:%M:%S")
    
    # 2. Convert container to ID3v2.4 and write the TDEN frame
    eyeD3 --to-v2.4 --preserve-file-times --text-frame="TDEN:$mod_time" "$file"
    eyeD3 --to-v2.4 --preserve-file-times --user-text-frame="original_mtime:$mod_time" "$file"
done
