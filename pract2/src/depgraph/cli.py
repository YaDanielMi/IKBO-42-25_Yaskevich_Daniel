"""Command line interface of the dependency graph tool."""

import argparse
import sys
from dataclasses import asdict

from depgraph.config import DEFAULT_OUTPUT, build_config
from depgraph.errors import DepGraphError

EXIT_OK = 0
EXIT_ERROR = 1


def create_parser():
    """Create the parser with all user configurable parameters."""
    parser = argparse.ArgumentParser(
        prog="depgraph",
        description="Dependency graph visualiser for npm packages.",
    )
    parser.add_argument(
        "-p", "--package", required=True,
        help="name of the analysed package",
    )
    parser.add_argument(
        "-r", "--repo", default=None,
        help="repository URL (default: the public npm registry); "
        "in test mode: path to the test repository file",
    )
    parser.add_argument(
        "-t", "--test-mode", action="store_true",
        help="work with a test repository described in a file",
    )
    parser.add_argument(
        "-o", "--output", default=DEFAULT_OUTPUT,
        help="name of the generated PNG file (default: %(default)s)",
    )
    parser.add_argument(
        "-a", "--ascii-tree", action="store_true",
        help="print the dependencies as an ASCII tree",
    )
    parser.add_argument(
        "-f", "--filter", default="", dest="filter_substring",
        help="ignore packages whose name contains this substring",
    )
    return parser


def format_config(config):
    """Return the parameters as ``key: value`` lines."""
    lines = []
    for key, value in asdict(config).items():
        text = str(value).lower() if isinstance(value, bool) else value
        lines.append(f"{key}: {text}")
    return lines


def main(argv=None):
    """Run the tool and return the process exit code."""
    args = create_parser().parse_args(argv)
    try:
        config = build_config(args)
    except DepGraphError as error:
        print(f"error: {error}", file=sys.stderr)
        return EXIT_ERROR
    print("\n".join(format_config(config)))
    return EXIT_OK
