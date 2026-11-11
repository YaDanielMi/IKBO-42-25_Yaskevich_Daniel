"""Tests for the ASCII tree output."""

import unittest

from depgraph.ascii_tree import render_tree
from depgraph.file_repository import FileRepository
from depgraph.graph import build_dependency_graph


def tree(text, root):
    """Render the tree of a test repository given as text."""
    repository = FileRepository.from_text(text)
    return render_tree(build_dependency_graph(repository, root), root)


class AsciiTreeTests(unittest.TestCase):
    """Rendering of trees, shared packages and cycles."""

    def test_single_package(self):
        """A package without dependencies is just its name."""
        self.assertEqual(tree("A:\n", "A"), ["A"])

    def test_chain(self):
        """Each level is indented under its parent."""
        self.assertEqual(
            tree("A: B\nB: C\nC:\n", "A"),
            ["A", "`-- B", "    `-- C"],
        )

    def test_branches(self):
        """Non-last children use a branch and a vertical line."""
        self.assertEqual(
            tree("A: B C\nB: D\nC:\nD:\n", "A"),
            ["A", "|-- B", "|   `-- D", "`-- C"],
        )

    def test_shared_dependency_is_marked(self):
        """A subtree that is already shown is not expanded again."""
        lines = tree("A: B C\nB: D\nC: D\nD: E\nE:\n", "A")
        self.assertEqual(
            lines,
            ["A", "|-- B", "|   `-- D", "|       `-- E", "`-- C",
             "    `-- D (*)"],
        )

    def test_cycle_is_marked(self):
        """A package that closes a cycle is marked and not expanded."""
        lines = tree("A: B\nB: A\n", "A")
        self.assertEqual(lines, ["A", "`-- B", "    `-- A (cycle)"])

    def test_self_loop(self):
        """A self-dependency is a cycle of length one."""
        self.assertEqual(tree("A: A\n", "A"), ["A", "`-- A (cycle)"])

    def test_only_ascii_characters(self):
        """The output contains only ASCII characters."""
        text = "\n".join(tree("A: B C\nB: C\nC: A\n", "A"))
        self.assertTrue(text.isascii())

    def test_deep_tree_without_recursion(self):
        """A deep chain does not overflow the call stack."""
        depth = 3000
        graph = {index: [index + 1] for index in range(depth)}
        graph[depth] = []
        lines = render_tree({str(k): [str(v) for v in vs]
                             for k, vs in graph.items()}, "0")
        self.assertEqual(len(lines), depth + 1)


if __name__ == "__main__":
    unittest.main()
