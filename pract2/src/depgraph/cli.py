"""Command line interface of the dependency graph tool."""

import argparse
import sys

from depgraph.config import DEFAULT_OUTPUT, build_config
from depgraph.errors import DepGraphError
from depgraph.graph import build_dependency_graph
from depgraph.repository import open_repository

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


def print_graph(graph, root):
    """Print the dependency graph as adjacency lines."""
    print(f"Dependencies of {root}: {len(graph) - 1} package(s)")
    for name, dependencies in graph.items():
        targets = ", ".join(dependencies) or "(none)"
        print(f"  {name} -> {targets}")


def run(config):
    """Build the dependency graph and print it."""
    repository = open_repository(config)
    graph = build_dependency_graph(
        repository, config.package, config.filter_substring
    )
    print_graph(graph, config.package)


def main(argv=None):
    """Run the tool and return the process exit code."""
    args = create_parser().parse_args(argv)
    try:
        config = build_config(args)
        run(config)
    except DepGraphError as error:
        print(f"error: {error}", file=sys.stderr)
        return EXIT_ERROR
    return EXIT_OK
