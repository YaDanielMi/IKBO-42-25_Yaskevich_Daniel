"""Tests for the test repository stored in a text file."""

import os
import tempfile
import unittest

from depgraph.errors import PackageNotFoundError, RepositoryError
from depgraph.file_repository import FileRepository, parse_graph


class ParseGraphTests(unittest.TestCase):
    """Parsing of the description text."""

    def test_simple_graph(self):
        """Dependencies are read in the order of the description."""
        graph = parse_graph("A: C B\nB: C\nC:\n")
        self.assertEqual(graph, {"A": ["C", "B"], "B": ["C"], "C": []})

    def test_comments_and_blank_lines(self):
        """Comments and empty lines are ignored."""
        self.assertEqual(parse_graph("# note\n\nA:\n"), {"A": []})

    def test_undeclared_dependency(self):
        """A package that is only mentioned has no dependencies."""
        self.assertEqual(parse_graph("A: B\n"), {"A": ["B"], "B": []})

    def test_duplicate_dependencies_are_merged(self):
        """The same dependency listed twice is kept once."""
        self.assertEqual(parse_graph("A: B B\n")["A"], ["B"])

    def test_errors(self):
        """Malformed descriptions are rejected with a line number."""
        broken = ("A B\n", "a: B\n", "A: b\n", ": A\n", "A:\nA: B\n")
        for text in broken:
            with self.subTest(text=text):
                with self.assertRaises(RepositoryError):
                    parse_graph(text)


class FileRepositoryTests(unittest.TestCase):
    """Reading dependencies from the repository object."""

    def test_dependencies_and_packages(self):
        """The interface of the repository works on parsed text."""
        repository = FileRepository.from_text("A: B\nB:\n")
        self.assertEqual(repository.dependencies("A"), ["B"])
        self.assertEqual(repository.packages(), ["A", "B"])

    def test_unknown_package(self):
        """An unknown package is reported."""
        with self.assertRaises(PackageNotFoundError):
            FileRepository.from_text("A:\n").dependencies("Z")

    def test_from_file(self):
        """The description is loaded from a file."""
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "repo.txt")
            with open(path, "w", encoding="utf-8") as file:
                file.write("A: B\n")
            repository = FileRepository.from_file(path)
        self.assertEqual(repository.dependencies("A"), ["B"])

    def test_unreadable_file(self):
        """A file that cannot be read is a repository error."""
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(RepositoryError):
                FileRepository.from_file(directory)
            path = os.path.join(directory, "binary.txt")
            with open(path, "wb") as file:
                file.write(b"\xff\xfe\x00")
            with self.assertRaises(RepositoryError):
                FileRepository.from_file(path)


if __name__ == "__main__":
    unittest.main()
