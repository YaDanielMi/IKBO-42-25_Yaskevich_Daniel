#!/bin/bash
dir="$1"
if [ -z "$dir" ]; then
    dir="."
fi

find "$dir" -type f -exec md5sum {} \; | sort > /tmp/hashes_$$.txt

prev_hash=""
prev_file=""

while read -r hash file; do
    if [ "$hash" = "$prev_hash" ]; then
        echo "$prev_file"
        echo "$file"
    fi
    prev_hash="$hash"
    prev_file="$file"
done < /tmp/hashes_$$.txt

rm /tmp/hashes_$$.txt
