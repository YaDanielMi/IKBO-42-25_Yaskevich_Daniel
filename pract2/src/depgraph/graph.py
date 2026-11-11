"""Construction of the dependency graph.

A graph is a dictionary ``package -> list of its dependencies``. It is
built with a breadth-first search (BFS) that uses a queue instead of
recursion, so cyclic dependencies and very deep graphs are handled.
"""

from collections import deque

from depgraph.errors import ConfigError


def is_excluded(name, substring):
    """Tell whether the package must be ignored by the filter."""
    return bool(substring) and substring in name


def bfs_graph(root, neighbours):
    """Traverse the graph from the root in breadth-first order.

    ``neighbours(name)`` returns the packages that follow the given one.
    Every package is visited once, which makes cycles harmless.
    """
    graph = {}
    visited = {root}
    queue = deque([root])
    while queue:
        current = queue.popleft()
        children = neighbours(current)
        graph[current] = children
        for child in children:
            if child not in visited:
                visited.add(child)
                queue.append(child)
    return graph


def check_not_excluded(name, substring):
    """Refuse to analyse a package that the filter removes."""
    if is_excluded(name, substring):
        raise ConfigError(
            f"package {name!r} contains the filter substring {substring!r}"
        )


def build_dependency_graph(repository, root, substring=""):
    """Build the transitive dependency graph of the root package."""
    check_not_excluded(root, substring)

    def neighbours(name):
        """Direct dependencies that are not removed by the filter."""
        return [
            dependency
            for dependency in repository.dependencies(name)
            if not is_excluded(dependency, substring)
        ]

    return bfs_graph(root, neighbours)
