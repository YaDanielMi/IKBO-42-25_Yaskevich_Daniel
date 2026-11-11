#!/bin/sh
# Compare the packages found by depgraph with the output of `npm ls`.
# Usage: scripts/compare.sh express
# Needs npm and network access; npm is used only for the comparison.
set -eu
PKG="${1:?usage: scripts/compare.sh PACKAGE}"
DIR=$(cd "$(dirname "$0")/.." && pwd)
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

npm install --prefix "$TMP" --ignore-scripts --no-audit --no-fund "$PKG" \
    > /dev/null
npm ls --all --parseable --prefix "$TMP" \
    | sed -n 's#.*/node_modules/##p' | sort -u > "$TMP/npm.txt"
"$DIR/run.sh" -p "$PKG" -o "$TMP/graph.png" 2> /dev/null \
    | sed -n 's/^  \([^ ]*\) -> .*/\1/p' | sort -u > "$TMP/depgraph.txt" \
    || true

echo "npm ls: $(wc -l < "$TMP/npm.txt") packages," \
    "depgraph: $(wc -l < "$TMP/depgraph.txt") packages"
echo "--- only in npm ls:"
comm -23 "$TMP/npm.txt" "$TMP/depgraph.txt"
echo "--- only in depgraph:"
comm -13 "$TMP/npm.txt" "$TMP/depgraph.txt"
