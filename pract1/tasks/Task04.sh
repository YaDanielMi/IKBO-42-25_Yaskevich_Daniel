#!/bin/bash
file="$1"
grep -oE "[a-zA-Z_][a-zA-Z0-9_]*" "$file" | sort -u | tr "\n" " "
echo ""
