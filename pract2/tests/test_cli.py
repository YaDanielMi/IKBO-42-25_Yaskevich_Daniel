"""Tests for the command line interface (stage 1)."""

import contextlib
import io
import unittest

from depgraph.cli import EXIT_ERROR, EXIT_OK, main

USAGE_ERROR = 2


def run_cli(argv):
    """Run main() and return the exit code with captured output."""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            code = main(argv)
        except SystemExit as exit_info:
            code = exit_info.code
    return code, out.getvalue(), err.getvalue()


class ParametersOutputTests(unittest.TestCase):
    """The tool prints all parameters as key-value pairs."""

    def test_defaults(self):
        """Default values are printed when only a package is given."""
        code, out, _ = run_cli(["-p", "express"])
        self.assertEqual(code, EXIT_OK)
        self.assertEqual(
            out.splitlines(),
            [
                "package: express",
                "repo: https://registry.npmjs.org",
                "test_mode: false",
                "output: graph.png",
                "ascii_tree: false",
                "filter_substring: ",
            ],
        )

    def test_all_parameters(self):
        """Every parameter given by the user is reflected in the output."""
        code, out, _ = run_cli(
            ["-p", "react", "-r", "http://localhost:4873", "-o", "g.png",
             "-a", "-f", "babel"]
        )
        self.assertEqual(code, EXIT_OK)
        self.assertIn("package: react", out)
        self.assertIn("repo: http://localhost:4873", out)
        self.assertIn("output: g.png", out)
        self.assertIn("ascii_tree: true", out)
        self.assertIn("filter_substring: babel", out)


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
