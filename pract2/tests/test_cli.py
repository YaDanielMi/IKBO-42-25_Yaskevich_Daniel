"""Tests for the command line interface."""

import contextlib
import io
import os
import tempfile
import unittest
from unittest import mock

from depgraph.cli import EXIT_ERROR, EXIT_OK, main
from depgraph.errors import PackageNotFoundError

USAGE_ERROR = 2
REPOSITORY = "depgraph.repository.NpmRepository"


def run_cli(argv):
    """Run main() and return the exit code with captured output."""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            code = main(argv)
        except SystemExit as exit_info:
            code = exit_info.code
    return code, out.getvalue(), err.getvalue()


class TestModeTests(unittest.TestCase):
    """The tool works with a test repository file."""

    def run_on(self, text, *extra):
        """Run the tool on a test repository given as text."""
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "repo.txt")
            with open(path, "w", encoding="utf-8") as file:
                file.write(text)
            return run_cli(["-t", "-r", path, *extra])

    def test_prints_graph(self):
        """The transitive graph is printed as adjacency lines."""
        code, out, _ = self.run_on("A: B C\nB: C\nC:\n", "-p", "A")
        self.assertEqual(code, EXIT_OK)
        self.assertEqual(
            out.splitlines(),
            [
                "Dependencies of A: 2 package(s)",
                "  A -> B, C",
                "  B -> C",
                "  C -> (none)",
            ],
        )

    def test_cycle(self):
        """A cyclic graph is printed and the tool terminates."""
        code, out, _ = self.run_on("A: B\nB: A\n", "-p", "A")
        self.assertEqual(code, EXIT_OK)
        self.assertIn("  B -> A", out)

    def test_filter(self):
        """The filter option removes packages from the graph."""
        _, out, _ = self.run_on("A: B C\nB:\nC:\n", "-p", "A", "-f", "B")
        self.assertEqual(
            out.splitlines(),
            ["Dependencies of A: 1 package(s)", "  A -> C", "  C -> (none)"],
        )

    def test_reverse_dependencies(self):
        """The reverse option prints the packages that depend on -p."""
        code, out, _ = self.run_on(
            "A: B C\nB: C\nC:\n", "-p", "C", "--reverse"
        )
        self.assertEqual(code, EXIT_OK)
        self.assertEqual(
            out.splitlines(),
            [
                "Reverse dependencies of C: 2 package(s)",
                "  C <- A, B",
                "  A <- (none)",
                "  B <- A",
            ],
        )

    def test_unknown_package(self):
        """A package missing in the test repository is an error."""
        code, out, err = self.run_on("A:\n", "-p", "Z")
        self.assertEqual(code, EXIT_ERROR)
        self.assertEqual(out, "")
        self.assertIn("not found", err)

    def test_broken_repository(self):
        """A malformed repository file is an error."""
        code, _, err = self.run_on("oops\n", "-p", "A")
        self.assertEqual(code, EXIT_ERROR)
        self.assertIn("line 1", err)

    def test_filtered_package(self):
        """Filtering out the analysed package is an error."""
        code, _, err = self.run_on("A:\n", "-p", "A", "-f", "A")
        self.assertEqual(code, EXIT_ERROR)
        self.assertIn("filter substring", err)


class NpmModeTests(unittest.TestCase):
    """The tool prints the graph of an npm package."""

    def test_repository_error(self):
        """Repository failures are printed as errors."""
        repository = mock.Mock()
        repository.dependencies.side_effect = PackageNotFoundError("gone")
        with mock.patch(REPOSITORY, return_value=repository):
            code, out, err = run_cli(["-p", "nothing"])
        self.assertEqual(code, EXIT_ERROR)
        self.assertEqual(out, "")
        self.assertIn("error: gone", err)

    def test_reverse_is_not_available(self):
        """An npm registry cannot provide reverse dependencies."""
        code, _, err = run_cli(["-p", "express", "--reverse"])
        self.assertEqual(code, EXIT_ERROR)
        self.assertIn("only in test mode", err)

    def test_prints_graph(self):
        """Dependencies returned by the registry form the graph."""
        repository = mock.Mock()
        repository.dependencies.side_effect = lambda name: {
            "express": ["qs"], "qs": []}[name]
        with mock.patch(REPOSITORY, return_value=repository):
            code, out, _ = run_cli(["-p", "express"])
        self.assertEqual(code, EXIT_OK)
        self.assertIn("  express -> qs", out)


class ErrorHandlingTests(unittest.TestCase):
    """Each parameter has its own error handling."""

    def assert_error(self, argv, fragment):
        """Check exit code and that stderr mentions the fragment."""
        code, out, err = run_cli(argv)
        self.assertEqual(code, EXIT_ERROR)
        self.assertEqual(out, "")
        self.assertIn(fragment, err)

    def test_missing_package(self):
        """The package parameter is mandatory."""
        code, _, err = run_cli([])
        self.assertEqual(code, USAGE_ERROR)
        self.assertIn("--package", err)

    def test_bad_package(self):
        """An invalid package name is reported."""
        self.assert_error(["-p", "Bad Name"], "invalid package name")

    def test_bad_url(self):
        """An invalid repository URL is reported."""
        self.assert_error(["-p", "x", "-r", "ftp://h"], "repository URL")

    def test_missing_test_repo_file(self):
        """A missing test repository file is reported."""
        self.assert_error(
            ["-p", "A", "-t", "-r", "/no/such/file.txt"], "not found"
        )

    def test_test_mode_without_repo(self):
        """Test mode requires an explicit repository file."""
        self.assert_error(["-p", "A", "-t"], "--repo is required")

    def test_bad_output(self):
        """A non-png output name is reported."""
        self.assert_error(["-p", "x", "-o", "g.jpg"], "output file")

    def test_bad_filter(self):
        """A filter with whitespace is reported."""
        self.assert_error(["-p", "x", "-f", "a b"], "whitespace")


if __name__ == "__main__":
    unittest.main()
