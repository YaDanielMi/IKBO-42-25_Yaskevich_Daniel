"""Tests for validation of the user supplied parameters."""

import os
import tempfile
import unittest
from argparse import Namespace

from depgraph.config import (
    DEFAULT_REGISTRY,
    build_config,
    validate_output,
    validate_package,
    validate_repo,
    validate_substring,
)
from depgraph.errors import ConfigError


def make_args(**overrides):
    """Build a parsed-arguments object filled with valid defaults."""
    values = {
        "package": "express",
        "repo": None,
        "test_mode": False,
        "output": "graph.png",
        "ascii_tree": False,
        "filter_substring": "",
        "reverse": False,
    }
    values.update(overrides)
    return Namespace(**values)


class PackageNameTests(unittest.TestCase):
    """Validation of the package name."""

    def test_valid_npm_names(self):
        """Ordinary and scoped npm names are accepted."""
        for name in ("express", "@types/node", "lodash.merge", "a-b_c"):
            with self.subTest(name=name):
                self.assertEqual(validate_package(name, False), name)

    def test_invalid_npm_names(self):
        """Empty names, spaces, capitals and paths are rejected."""
        for name in ("", "   ", "Express", "has space", "../x", "a/b"):
            with self.subTest(name=name):
                with self.assertRaises(ConfigError):
                    validate_package(name, False)

    def test_test_mode_names(self):
        """In test mode only uppercase Latin letters are allowed."""
        for name in ("A", "AB"):
            self.assertEqual(validate_package(name, True), name)
        for name in ("a", "A1", "express", "A-B"):
            with self.subTest(name=name):
                with self.assertRaises(ConfigError):
                    validate_package(name, True)


class RepoTests(unittest.TestCase):
    """Validation of the repository location."""

    def test_valid_urls(self):
        """Both http and https URLs are accepted."""
        for url in ("https://registry.npmjs.org", "http://localhost:4873/"):
            self.assertEqual(validate_repo(url, False), url)

    def test_invalid_urls(self):
        """Other schemes, missing hosts and empty values are rejected."""
        for url in ("", "ftp://host", "registry.npmjs.org", "https://"):
            with self.subTest(url=url):
                with self.assertRaises(ConfigError):
                    validate_repo(url, False)

    def test_test_repo_file(self):
        """An existing file is accepted, a missing one or a dir is not."""
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "repo.txt")
            with open(path, "w", encoding="utf-8") as file:
                file.write("A:\n")
            self.assertEqual(validate_repo(path, True), path)
            with self.assertRaises(ConfigError):
                validate_repo(os.path.join(directory, "none.txt"), True)
            with self.assertRaises(ConfigError):
                validate_repo(directory, True)


class OutputTests(unittest.TestCase):
    """Validation of the image file name."""

    def test_valid_output(self):
        """A png file name in an existing directory is accepted."""
        self.assertEqual(validate_output("graph.png"), "graph.png")
        self.assertEqual(validate_output("GRAPH.PNG"), "GRAPH.PNG")

    def test_invalid_output(self):
        """Wrong extension, bare extension and bad directory fail."""
        for name in ("", "graph.jpg", "graph", ".png", "no/such/dir/g.png"):
            with self.subTest(name=name):
                with self.assertRaises(ConfigError):
                    validate_output(name)

    def test_directory_is_rejected(self):
        """A directory cannot be used as the output file."""
        with tempfile.TemporaryDirectory() as directory:
            target = os.path.join(directory, "x.png")
            os.mkdir(target)
            with self.assertRaises(ConfigError):
                validate_output(target)


class SubstringTests(unittest.TestCase):
    """Validation of the filter substring."""

    def test_valid_substring(self):
        """Empty and ordinary substrings are accepted."""
        self.assertEqual(validate_substring(""), "")
        self.assertEqual(validate_substring("babel"), "babel")

    def test_whitespace_is_rejected(self):
        """Package names never contain whitespace."""
        with self.assertRaises(ConfigError):
            validate_substring("a b")


class BuildConfigTests(unittest.TestCase):
    """Creation of the whole configuration."""

    def test_default_registry(self):
        """The public npm registry is used when no repo is given."""
        self.assertEqual(build_config(make_args()).repo, DEFAULT_REGISTRY)

    def test_repo_required_in_test_mode(self):
        """Test mode without a repository file is an error."""
        with self.assertRaises(ConfigError):
            build_config(make_args(package="A", test_mode=True))
