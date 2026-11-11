#!/bin/sh
# Run the tool: ./run.sh -p express
DIR=$(cd "$(dirname "$0")" && pwd)
PYTHONPATH="$DIR/src" exec python3 -m depgraph "$@"
