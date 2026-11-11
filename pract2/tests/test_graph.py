"""Tests for the dependency graph construction (BFS)."""

import unittest

from depgraph.errors import ConfigError, PackageNotFoundError
from depgraph.file_repository import FileRepository
from depgraph.graph import bfs_graph, build_dependency_graph


def build(text, root, substring=""):
    """Build a graph from a test repository given as text."""
    repository = FileRepository.from_text(text)
    return build_dependency_graph(repository, root, substring)


class TransitiveGraphTests(unittest.TestCase):
    """Transitive dependencies in different kinds of graphs."""

    def test_isolated_package(self):
        """A package without dependencies gives a single node."""
        self.assertEqual(build("A:\n", "A"), {"A": []})

    def test_chain(self):
        """Transitive dependencies of a chain are all found."""
        graph = build("A: B\nB: C\nC: D\nD:\n", "A")
        self.assertEqual(list(graph), ["A", "B", "C", "D"])

    def test_diamond(self):
        """A shared dependency is visited only once."""
        graph = build("A: B C\nB: D\nC: D\nD:\n", "A")
        self.assertEqual(
            graph, {"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": []}
        )

    def test_bfs_order(self):
        """Packages are discovered level by level."""
        graph = build("A: B C\nB: D\nC: E\nD:\nE:\n", "A")
        self.assertEqual(list(graph), ["A", "B", "C", "D", "E"])

    def test_root_is_a_subgraph(self):
        """Only packages reachable from the root are included."""
        graph = build("A: B\nB:\nC: A\n", "B")
        self.assertEqual(graph, {"B": []})

    def test_deep_chain_without_recursion(self):
        """A very deep graph does not overflow the call stack."""
        depth = 5000

        def neighbours(node):
            """Each node points to the next one, the last has no edges."""
            return [node + 1] if node < depth - 1 else []

        self.assertEqual(len(bfs_graph(0, neighbours)), depth)


class CycleTests(unittest.TestCase):
    """Cyclic dependencies are processed correctly."""

    def test_cycle(self):
        """A cycle terminates and keeps the back edge."""
        graph = build("A: B\nB: C\nC: A D\nD:\n", "A")
        self.assertEqual(graph["C"], ["A", "D"])
        self.assertEqual(set(graph), {"A", "B", "C", "D"})

    def test_self_loop(self):
        """A package that depends on itself terminates."""
        graph = build("A: A B\nB:\n", "A")
        self.assertEqual(graph, {"A": ["A", "B"], "B": []})

    def test_mutual_dependency(self):
        """Two packages depending on each other terminate."""
        graph = build("A: B\nB: A\n", "B")
        self.assertEqual(graph, {"B": ["A"], "A": ["B"]})


class FilterTests(unittest.TestCase):
    """Packages whose name contains the substring are ignored."""

    TEXT = "A: AB BC C\nAB: C\nBC: AB D\nC:\nD:\n"

    def test_filter_removes_packages_and_their_subtrees(self):
        """Excluded packages and what only they bring are not visited."""
        graph = build(self.TEXT, "A", "B")
        self.assertEqual(graph, {"A": ["C"], "C": []})

    def test_empty_filter_keeps_everything(self):
        """An empty substring does not exclude anything."""
        self.assertEqual(len(build(self.TEXT, "A")), 5)

    def test_filter_is_case_sensitive(self):
        """The substring is compared as is."""
        self.assertEqual(len(build(self.TEXT, "A", "b")), 5)

    def test_filtered_root_is_an_error(self):
        """The analysed package itself cannot be filtered out."""
        with self.assertRaises(ConfigError):
            build(self.TEXT, "AB", "B")

    def test_unknown_root(self):
        """An unknown package is reported."""
        with self.assertRaises(PackageNotFoundError):
            build(self.TEXT, "Z")


if __name__ == "__main__":
    unittest.main()
