#!/bin/bash
dir="$1"
if [ -z "$dir" ]; then
    dir="."
fi

find "$dir" -maxdepth 1 -type f -empty
