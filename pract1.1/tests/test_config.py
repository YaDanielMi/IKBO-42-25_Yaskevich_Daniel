"""Tests of command line parameters."""
import os
import tempfile
import unittest

from config import (
    ConfigError, Config, NOT_SET, debug_lines, parse_args, validate,
)


class ParseArgsTest(unittest.TestCase):
    """Parsing of argv into Config."""

    def test_defaults(self):
        self.assertEqual(parse_args([]), Config())

    def test_all_parameters(self):
        config = parse_args(
            ["--vfs", "d", "--script", "s.emu", "--headless"]
        )
        self.assertEqual(config, Config("d", "s.emu", True))

    def test_unknown_parameter_exits(self):
        with self.assertRaises(SystemExit):
            parse_args(["--bogus"])

    def test_missing_value_exits(self):
        with self.assertRaises(SystemExit):
            parse_args(["--vfs"])


class DebugLinesTest(unittest.TestCase):
    """Debug output of the parameters."""

    def test_unset_parameters(self):
        text = "\n".join(debug_lines(Config()))
        self.assertIn(NOT_SET, text)
        self.assertIn("--headless = False", text)

    def test_given_parameters_are_listed(self):
        text = "\n".join(debug_lines(Config("some/dir", "a.emu", True)))
        self.assertIn("some/dir", text)
        self.assertIn(os.path.abspath("a.emu"), text)
        self.assertIn("--headless = True", text)


class ValidateTest(unittest.TestCase):
    """Validation of paths."""

    def test_valid_paths(self):
        with tempfile.TemporaryDirectory() as folder:
            script = os.path.join(folder, "s.emu")
            open(script, "w").close()
            validate(Config(folder, script))

    def test_missing_vfs(self):
        with self.assertRaises(ConfigError):
            validate(Config(vfs_path="/no/such/dir"))

    def test_vfs_is_a_file(self):
        with tempfile.NamedTemporaryFile() as handle:
            with self.assertRaises(ConfigError):
                validate(Config(vfs_path=handle.name))

    def test_missing_script(self):
        with self.assertRaises(ConfigError):
            validate(Config(script_path="/no/such/script"))


if __name__ == "__main__":
    unittest.main()
