#!/bin/bash
text="$1"
length=${#text}

line=""
i=0
while [ $i -lt $((length + 2)) ]; do
    line="$line-"
    i=$((i + 1))
done

echo "+$line+"
echo "| $text |"
echo "+$line+"
