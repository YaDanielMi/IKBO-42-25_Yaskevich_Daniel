"""Command line interface of the dependency graph tool."""

import argparse
import sys

from depgraph.config import DEFAULT_OUTPUT, build_config
from depgraph.errors import ConfigError, DepGraphError
from depgraph.npm_repository import NpmRepository

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


def print_direct_dependencies(config):
    """Print the direct dependencies of the package (stage 2 only)."""
    if config.test_mode:
        raise ConfigError("test mode is not supported yet")
    repository = NpmRepository(config.repo)
    dependencies = repository.dependencies(config.package)
    print(f"Direct dependencies of {config.package}:")
    for name in dependencies:
        print(f"  {name}")
    if not dependencies:
        print("  (none)")


def main(argv=None):
    """Run the tool and return the process exit code."""
    args = create_parser().parse_args(argv)
    try:
        config = build_config(args)
        print_direct_dependencies(config)
    except DepGraphError as error:
        print(f"error: {error}", file=sys.stderr)
        return EXIT_ERROR
    return EXIT_OK
