"""User configurable parameters and their validation."""

import os
import re
from dataclasses import dataclass
from urllib.parse import urlparse

from depgraph.errors import ConfigError

DEFAULT_REGISTRY = "https://registry.npmjs.org"
DEFAULT_OUTPUT = "graph.png"
OUTPUT_EXTENSION = ".png"
URL_SCHEMES = ("http", "https")
MAX_NPM_NAME_LENGTH = 214
NPM_NAME_RE = re.compile(
    r"^(@[a-z0-9-~][a-z0-9-._~]*/)?[a-z0-9-~][a-z0-9-._~]*$"
)
TEST_NAME_RE = re.compile(r"^[A-Z]+$")


@dataclass(frozen=True)
class Config:
    """All parameters that the user can set from the command line."""

    package: str
    repo: str
    test_mode: bool
    output: str
    ascii_tree: bool
    filter_substring: str


def validate_package(name, test_mode):
    """Check the package name for the selected kind of repository."""
    if not name or not name.strip():
        raise ConfigError("package name must not be empty")
    pattern = TEST_NAME_RE if test_mode else NPM_NAME_RE
    if not pattern.match(name) or len(name) > MAX_NPM_NAME_LENGTH:
        expected = "uppercase Latin letters" if test_mode else "an npm name"
        raise ConfigError(f"invalid package name {name!r}: expected {expected}")
    return name


def _check_test_repo_path(path):
    """Check that the test repository file exists and can be read."""
    if not os.path.exists(path):
        raise ConfigError(f"test repository file not found: {path}")
    if not os.path.isfile(path):
        raise ConfigError(f"test repository is not a file: {path}")
    if not os.access(path, os.R_OK):
        raise ConfigError(f"test repository is not readable: {path}")


def _check_repo_url(url):
    """Check that the repository URL is an http(s) URL with a host."""
    parsed = urlparse(url)
    if parsed.scheme not in URL_SCHEMES or not parsed.netloc:
        raise ConfigError(
            f"invalid repository URL {url!r}: expected http(s)://host[/path]"
        )


def validate_repo(repo, test_mode):
    """Check the repository location (file path in test mode, else URL)."""
    if not repo or not repo.strip():
        raise ConfigError("repository must not be empty")
    if test_mode:
        _check_test_repo_path(repo)
    else:
        _check_repo_url(repo)
    return repo


def validate_output(output):
    """Check the name of the image file that will be generated."""
    if not output or not output.strip():
        raise ConfigError("output file name must not be empty")
    name = os.path.basename(output)
    if name.lower() == OUTPUT_EXTENSION or not name.lower().endswith(
        OUTPUT_EXTENSION
    ):
        raise ConfigError(
            f"invalid output file {output!r}: expected name{OUTPUT_EXTENSION}"
        )
    directory = os.path.dirname(output) or "."
    if os.path.isdir(output):
        raise ConfigError(f"output path is a directory: {output}")
    if not os.path.isdir(directory):
        raise ConfigError(f"output directory does not exist: {directory}")
    if not os.access(directory, os.W_OK):
        raise ConfigError(f"output directory is not writable: {directory}")
    return output


def validate_substring(substring):
    """Check the substring used to filter packages."""
    if any(char.isspace() for char in substring):
        raise ConfigError("filter substring must not contain whitespace")
    return substring


def build_config(args):
    """Create a validated Config from parsed command line arguments."""
    repo = args.repo
    if repo is None:
        if args.test_mode:
            raise ConfigError("--repo is required in test mode")
        repo = DEFAULT_REGISTRY
    return Config(
        package=validate_package(args.package, args.test_mode),
        repo=validate_repo(repo, args.test_mode),
        test_mode=args.test_mode,
        output=validate_output(args.output),
        ascii_tree=args.ascii_tree,
        filter_substring=validate_substring(args.filter_substring),
    )
