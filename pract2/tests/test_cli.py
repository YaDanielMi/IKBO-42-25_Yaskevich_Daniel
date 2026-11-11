"""Tests for the command line interface."""

import contextlib
import io
import unittest
from unittest import mock

from depgraph.cli import EXIT_ERROR, EXIT_OK, main
from depgraph.errors import PackageNotFoundError

USAGE_ERROR = 2
REPOSITORY = "depgraph.cli.NpmRepository"


def run_cli(argv):
    """Run main() and return the exit code with captured output."""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            code = main(argv)
        except SystemExit as exit_info:
            code = exit_info.code
    return code, out.getvalue(), err.getvalue()


class DirectDependenciesTests(unittest.TestCase):
    """The tool prints the direct dependencies of a package."""

    def test_prints_dependencies(self):
        """Names returned by the repository are printed."""
        repository = mock.Mock()
        repository.dependencies.return_value = ["a", "b"]
        with mock.patch(REPOSITORY, return_value=repository):
            code, out, _ = run_cli(["-p", "express"])
        self.assertEqual(code, EXIT_OK)
        self.assertEqual(
            out.splitlines(),
            ["Direct dependencies of express:", "  a", "  b"],
        )

    def test_no_dependencies(self):
        """A package without dependencies is reported explicitly."""
        repository = mock.Mock()
        repository.dependencies.return_value = []
        with mock.patch(REPOSITORY, return_value=repository):
            _, out, _ = run_cli(["-p", "left-pad"])
        self.assertIn("(none)", out)

    def test_repository_error(self):
        """Repository failures are printed as errors."""
        repository = mock.Mock()
        repository.dependencies.side_effect = PackageNotFoundError("gone")
        with mock.patch(REPOSITORY, return_value=repository):
            code, out, err = run_cli(["-p", "nothing"])
        self.assertEqual(code, EXIT_ERROR)
        self.assertEqual(out, "")
        self.assertIn("error: gone", err)


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
