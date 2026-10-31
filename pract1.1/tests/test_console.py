"""Tests of the console (--headless) front end."""
import io
import unittest

from console import ConsoleView, run_headless
from shell import Shell


class HeadlessTest(unittest.TestCase):
    """Dialog through standard streams."""

    def run_emulator(self, stdin_text, script=()):
        """Run the console loop, return (exit code, stdout, stderr)."""
        streams = (io.StringIO(stdin_text), io.StringIO(), io.StringIO())
        view = ConsoleView(*streams)
        code = run_headless(Shell("u", "h"), view, list(script))
        return code, streams[1].getvalue(), streams[2].getvalue()

    def test_stdin_commands_are_echoed(self):
        code, out, _ = self.run_emulator("ls\nexit 5\n")
        self.assertEqual(code, 5)
        self.assertIn("u@h:/$ ls\n", out)
        self.assertIn("u@h:/$ exit 5\n", out)

    def test_end_of_input_acts_as_exit(self):
        code, out, _ = self.run_emulator("")
        self.assertEqual(code, 0)
        self.assertTrue(out.endswith("exit\n"))

    def test_errors_go_to_stderr(self):
        _, out, err = self.run_emulator("foo\n")
        self.assertIn("foo: команда не найдена", err)
        self.assertNotIn("команда не найдена", out)

    def test_script_exit_skips_stdin(self):
        code, out, _ = self.run_emulator("ls\n", ["exit 2"])
        self.assertEqual(code, 2)
        self.assertNotIn("заглушка", out)

    def test_script_without_exit_continues_with_stdin(self):
        code, out, _ = self.run_emulator("exit 6\n", ["ls"])
        self.assertEqual(code, 6)
        self.assertIn("ls: заглушка", out)


if __name__ == "__main__":
    unittest.main()
