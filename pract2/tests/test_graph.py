"""Tests for the dependency graph construction (BFS)."""

import unittest

from depgraph.errors import ConfigError, PackageNotFoundError
from depgraph.file_repository import FileRepository
from depgraph.graph import (
    bfs_graph,
    build_dependency_graph,
    build_reverse_graph,
)


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

    text = "A: AB BC C\nAB: C\nBC: AB D\nC:\nD:\n"

    def test_filter_removes_packages_and_their_subtrees(self):
        """Excluded packages and what only they bring are not visited."""
        graph = build(self.text, "A", "B")
        self.assertEqual(graph, {"A": ["C"], "C": []})

    def test_empty_filter_keeps_everything(self):
        """An empty substring does not exclude anything."""
        self.assertEqual(len(build(self.text, "A")), 5)

    def test_filter_is_case_sensitive(self):
        """The substring is compared as is."""
        self.assertEqual(len(build(self.text, "A", "b")), 5)

    def test_filtered_root_is_an_error(self):
        """The analysed package itself cannot be filtered out."""
        with self.assertRaises(ConfigError):
            build(self.text, "AB", "B")

    def test_unknown_root(self):
        """An unknown package is reported."""
        with self.assertRaises(PackageNotFoundError):
            build(self.text, "Z")


def build_reverse(text, target, substring=""):
    """Build a reverse graph from a test repository given as text."""
    repository = FileRepository.from_text(text)
    return build_reverse_graph(repository, target, substring)


class ReverseGraphTests(unittest.TestCase):
    """Packages that depend on the given package."""

    diamond = "A: B C\nB: D\nC: D\nD:\n"

    def test_package_nobody_depends_on(self):
        """The root of a graph has no reverse dependencies."""
        self.assertEqual(build_reverse(self.diamond, "A"), {"A": []})

    def test_direct_and_transitive(self):
        """Both direct and transitive dependents are found."""
        graph = build_reverse(self.diamond, "D")
        self.assertEqual(
            graph, {"D": ["B", "C"], "B": ["A"], "C": ["A"], "A": []}
        )

    def test_middle_of_a_chain(self):
        """Only the packages above the target are reported."""
        graph = build_reverse("A: B\nB: C\nC: D\nD:\n", "C")
        self.assertEqual(list(graph), ["C", "B", "A"])

    def test_cycle(self):
        """Cycles do not make the traversal endless."""
        graph = build_reverse("A: B\nB: C\nC: A D\nD:\n", "A")
        self.assertEqual(set(graph), {"A", "B", "C"})
        self.assertEqual(graph["A"], ["C"])

    def test_self_loop(self):
        """A self-dependency is reported once."""
        self.assertEqual(build_reverse("A: A\n", "A"), {"A": ["A"]})

    def test_filter(self):
        """Filtered packages are neither visited nor passed through."""
        text = "A: AB\nAB: C\nB: C\nC:\n"
        graph = build_reverse(text, "C", "A")
        self.assertEqual(graph, {"C": ["B"], "B": []})

    def test_filtered_target(self):
        """The analysed package cannot be filtered out."""
        with self.assertRaises(ConfigError):
            build_reverse("AB:\n", "AB", "B")

    def test_unknown_target(self):
        """An unknown package is reported."""
        with self.assertRaises(PackageNotFoundError):
            build_reverse("A:\n", "Z")


if __name__ == "__main__":
    unittest.main()
