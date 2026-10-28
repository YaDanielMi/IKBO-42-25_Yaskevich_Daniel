"""Tests of startup script reading and replaying."""
import os
import tempfile
import unittest

from helpers import RecordingView
from script import ScriptError, read_script, run_script
from shell import Shell


class ReadScriptTest(unittest.TestCase):
    """Reading script files."""

    def write(self, data):
        """Create a temporary script with the given bytes."""
        handle, path = tempfile.mkstemp()
        self.addCleanup(os.remove, path)
        with os.fdopen(handle, "wb") as stream:
            stream.write(data)
        return path

    def test_lines_crlf_and_bom(self):
        path = self.write("\ufeffls\r\ncd a\r\n".encode("utf-8"))
        self.assertEqual(read_script(path), ["ls", "cd a"])

    def test_missing_file(self):
        with self.assertRaises(ScriptError):
            read_script("/no/such/script")

    def test_bad_encoding(self):
        with self.assertRaises(ScriptError):
            read_script(self.write(b"\xff\xfe\x00bad\x80"))


class RunScriptTest(unittest.TestCase):
    """Replaying scripts as a dialog."""

    def setUp(self):
        self.shell = Shell("u", "h")
        self.view = RecordingView()

    def test_input_and_output_are_shown(self):
        run_script(self.shell, ["ls a"], self.view)
        self.assertEqual(self.view.kinds("echo"), ["ls a"])
        self.assertEqual(len(self.view.kinds("out")), 1)

    def test_comments_are_echoed_but_silent(self):
        run_script(self.shell, ["# note"], self.view)
        self.assertEqual(self.view.kinds("echo"), ["# note"])
        self.assertEqual(self.view.kinds("out"), [])

    def test_blank_lines_are_skipped(self):
        run_script(self.shell, ["", "   "], self.view)
        self.assertEqual(self.view.events, [])

    def test_errors_do_not_stop_the_script(self):
        run_script(self.shell, ["foo", "ls"], self.view)
        self.assertEqual(len(self.view.kinds("err")), 1)
        self.assertEqual(self.view.kinds("echo"), ["foo", "ls"])

    def test_exit_stops_the_script(self):
        result = run_script(self.shell, ["exit 4", "ls"], self.view)
        self.assertEqual(result.exit_code, 4)
        self.assertEqual(self.view.kinds("echo"), ["exit 4"])

    def test_no_exit_returns_none(self):
        self.assertIsNone(run_script(self.shell, ["ls"], self.view))


if __name__ == "__main__":
    unittest.main()
