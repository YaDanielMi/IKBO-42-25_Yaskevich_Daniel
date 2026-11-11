"""Test repository: a dependency graph described in a plain text file.

One package per line, the package name goes before the colon and its direct
dependencies after it::

    A: B C
    B: C
    C:

Package names are uppercase Latin letters. Empty lines and lines starting
with ``#`` are ignored. A package that is only mentioned as a dependency
has no dependencies of its own.
"""

import re

from depgraph.errors import PackageNotFoundError, RepositoryError

NAME_RE = re.compile(r"^[A-Z]+$")
COMMENT_PREFIX = "#"
SEPARATOR = ":"


def _parse_line(line, number):
    """Split a line into the package name and its dependencies."""
    name, separator, rest = line.partition(SEPARATOR)
    if not separator:
        raise RepositoryError(f"line {number}: expected '{SEPARATOR}'")
    name = name.strip()
    dependencies = rest.split()
    for item in [name] + dependencies:
        if not NAME_RE.match(item):
            raise RepositoryError(
                f"line {number}: invalid package name {item!r}"
            )
    return name, list(dict.fromkeys(dependencies))


def parse_graph(text):
    """Parse the text of a test repository into a dependency mapping."""
    graph = {}
    for number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith(COMMENT_PREFIX):
            continue
        name, dependencies = _parse_line(line, number)
        if name in graph:
            raise RepositoryError(
                f"line {number}: package {name} is defined twice"
            )
        graph[name] = dependencies
    for dependencies in list(graph.values()):
        for name in dependencies:
            graph.setdefault(name, [])
    return graph


class FileRepository:
    """Repository whose packages are described by a text file."""

    def __init__(self, graph):
        """Keep the mapping ``package -> list of direct dependencies``."""
        self._graph = graph

    @classmethod
    def from_text(cls, text):
        """Create a repository from the text of the description."""
        return cls(parse_graph(text))

    @classmethod
    def from_file(cls, path):
        """Create a repository from a description file."""
        try:
            with open(path, encoding="utf-8") as file:
                text = file.read()
        except (OSError, UnicodeDecodeError) as error:
            raise RepositoryError(
                f"cannot read test repository {path}: {error}"
            ) from error
        return cls.from_text(text)

    def dependencies(self, name):
        """Return the direct dependencies of a package."""
        if name not in self._graph:
            raise PackageNotFoundError(
                f"package {name!r} not found in the test repository"
            )
        return list(self._graph[name])

    def packages(self):
        """Return the names of all packages of the repository."""
        return list(self._graph)
