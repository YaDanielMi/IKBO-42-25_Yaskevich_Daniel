"""Tests for the command line interface."""

import contextlib
import io
import os
import tempfile
import unittest
from functools import cached_property
from unittest import mock

from depgraph.cli import EXIT_ERROR, EXIT_OK, main
from depgraph.errors import PackageNotFoundError, RenderError

USAGE_ERROR = 2
REPOSITORY = "depgraph.repository.NpmRepository"
RENDER = "depgraph.plantuml.render_png"


def run_cli(argv):
    """Run main() and return the exit code with captured output."""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            code = main(argv)
        except SystemExit as exit_info:
            code = exit_info.code
    return code, out.getvalue(), err.getvalue()


class WorkDirTestCase(unittest.TestCase):
    """Base class: a temporary directory and a mocked PNG renderer."""

    @cached_property
    def directory(self):
        """A temporary directory (removed after the test)."""
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        return directory.name

    @cached_property
    def render(self):
        """The mocked PNG renderer (patched until the test ends)."""
        patcher = mock.patch(RENDER)
        render = patcher.start()
        self.addCleanup(patcher.stop)
        return render

    def run_cli(self, argv):
        """Run main() with the PNG renderer already replaced."""
        self.assertIsNotNone(self.render)
        return run_cli(argv)

    def path(self, name):
        """Return the path of a file inside the temporary directory."""
        return os.path.join(self.directory, name)

    def run_on(self, text, *extra):
        """Run the tool in test mode on a repository given as text."""
        repo = self.path("repo.txt")
        with open(repo, "w", encoding="utf-8") as file:
            file.write(text)
        output = self.path("g.png")
        return self.run_cli(["-t", "-r", repo, "-o", output, *extra])


class TestModeTests(WorkDirTestCase):
    """The tool works with a test repository file."""

    def test_prints_graph(self):
        """The transitive graph is printed as adjacency lines."""
        code, out, _ = self.run_on("A: B C\nB: C\nC:\n", "-p", "A")
        self.assertEqual(code, EXIT_OK)
        self.assertEqual(
            out.splitlines()[:4],
            [
                "Dependencies of A: 2 package(s)",
                "  A -> B, C",
                "  B -> C",
                "  C -> (none)",
            ],
        )

    def test_saves_text_and_image(self):
        """The PlantUML text is saved and the PNG renderer is called."""
        _, out, _ = self.run_on("A: B\nB:\n", "-p", "A")
        with open(self.path("g.puml"), encoding="utf-8") as file:
            self.assertIn("n0 --> n1", file.read())
        self.render.assert_called_once()
        self.assertEqual(self.render.call_args.args[1], self.path("g.png"))
        self.assertIn("Graph image:", out)

    def test_ascii_tree(self):
        """The ASCII tree is printed only when it is requested."""
        text = "A: B C\nB: D\nC: D\nD:\n"
        _, with_tree, _ = self.run_on(text, "-p", "A", "-a")
        _, without_tree, _ = self.run_on(text, "-p", "A")
        self.assertIn("|-- B\n|   `-- D\n`-- C\n    `-- D (*)", with_tree)
        self.assertNotIn("`--", without_tree)

    def test_cycle(self):
        """A cyclic graph is printed and the tool terminates."""
        code, out, _ = self.run_on("A: B\nB: A\n", "-p", "A", "-a")
        self.assertEqual(code, EXIT_OK)
        self.assertIn("  B -> A", out)
        self.assertIn("`-- A (cycle)", out)

    def test_filter(self):
        """The filter option removes packages from the graph."""
        _, out, _ = self.run_on("A: B C\nB:\nC:\n", "-p", "A", "-f", "B")
        self.assertEqual(
            out.splitlines()[:3],
            ["Dependencies of A: 1 package(s)", "  A -> C", "  C -> (none)"],
        )

    def test_reverse_dependencies(self):
        """The reverse option prints the packages that depend on -p."""
        code, out, _ = self.run_on(
            "A: B C\nB: C\nC:\n", "-p", "C", "--reverse"
        )
        self.assertEqual(code, EXIT_OK)
        self.assertEqual(
            out.splitlines()[:4],
            [
                "Reverse dependencies of C: 2 package(s)",
                "  C <- A, B",
                "  A <- (none)",
                "  B <- A",
            ],
        )

    def test_reverse_image_arrows(self):
        """Arrows of a reverse graph still mean 'depends on'."""
        self.run_on("A: B\nB:\n", "-p", "B", "--reverse")
        with open(self.path("g.puml"), encoding="utf-8") as file:
            text = file.read()
        self.assertIn("n1 --> n0", text)

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

    def test_render_error(self):
        """A rendering failure is an error but the text is kept."""
        self.render.side_effect = RenderError("no PlantUML")
        code, _, err = self.run_on("A:\n", "-p", "A")
        self.assertEqual(code, EXIT_ERROR)
        self.assertIn("no PlantUML", err)
        self.assertTrue(os.path.exists(self.path("g.puml")))


class NpmModeTests(WorkDirTestCase):
    """The tool prints the graph of an npm package."""

    def test_repository_error(self):
        """Repository failures are printed as errors."""
        repository = mock.Mock()
        repository.dependencies.side_effect = PackageNotFoundError("gone")
        with mock.patch(REPOSITORY, return_value=repository):
            code, out, err = self.run_cli(["-p", "nothing"])
        self.assertEqual(code, EXIT_ERROR)
        self.assertEqual(out, "")
        self.assertIn("error: gone", err)

    def test_reverse_is_not_available(self):
        """An npm registry cannot provide reverse dependencies."""
        code, _, err = self.run_cli(["-p", "express", "--reverse"])
        self.assertEqual(code, EXIT_ERROR)
        self.assertIn("only in test mode", err)

    def test_prints_graph(self):
        """Dependencies returned by the registry form the graph."""
        repository = mock.Mock()
        repository.dependencies.side_effect = lambda name: {
            "express": ["qs"], "qs": []}[name]
        with mock.patch(REPOSITORY, return_value=repository):
            code, out, _ = self.run_cli(
                ["-p", "express", "-o", self.path("e.png")])
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

    def test_bad_test_package(self):
        """Test mode accepts only uppercase Latin package names."""
        self.assert_error(
            ["-p", "express", "-t", "-r", __file__], "uppercase Latin"
        )

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

    def test_bad_output_directory(self):
        """A missing output directory is reported."""
        self.assert_error(["-p", "x", "-o", "/no/dir/g.png"], "directory")

    def test_bad_filter(self):
        """A filter with whitespace is reported."""
        self.assert_error(["-p", "x", "-f", "a b"], "whitespace")


if __name__ == "__main__":
    unittest.main()
