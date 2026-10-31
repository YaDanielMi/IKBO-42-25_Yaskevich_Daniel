"""Tests of the shell dispatcher and built-in commands."""
import unittest

from shell import Shell


class ShellTest(unittest.TestCase):
    """Behaviour of Shell.execute at the REPL stage."""

    def setUp(self):
        """Create a shell without VFS."""
        self.shell = Shell("alice", "box")

    def test_prompt(self):
        self.assertEqual(self.shell.prompt(), "alice@box:/$ ")

    def test_ls_stub_prints_name_and_args(self):
        result = self.shell.execute('ls -l "my dir"')
        self.assertIn("ls", result.output)
        self.assertIn("['-l', 'my dir']", result.output)

    def test_cd_stub_prints_name_and_args(self):
        result = self.shell.execute("cd /tmp")
        self.assertIn("cd", result.output)
        self.assertIn("['/tmp']", result.output)

    def test_blank_line_does_nothing(self):
        result = self.shell.execute("   ")
        self.assertEqual((result.output, result.error), ("", ""))
        self.assertFalse(result.exit_requested)

    def test_unknown_command(self):
        result = self.shell.execute("foo bar")
        self.assertEqual(result.error, "foo: команда не найдена")

    def test_parse_error_is_reported(self):
        result = self.shell.execute('ls "x')
        self.assertIn("ошибка разбора", result.error)
        self.assertFalse(result.exit_requested)

    def test_exit_without_arguments(self):
        result = self.shell.execute("exit")
        self.assertTrue(result.exit_requested)
        self.assertEqual(result.exit_code, 0)

    def test_exit_with_code(self):
        result = self.shell.execute("exit 3")
        self.assertTrue(result.exit_requested)
        self.assertEqual(result.exit_code, 3)

    def test_exit_code_wraps_modulo_256(self):
        self.assertEqual(self.shell.execute("exit 257").exit_code, 1)

    def test_exit_with_bad_code(self):
        result = self.shell.execute("exit abc")
        self.assertTrue(result.exit_requested)
        self.assertIn("числовой аргумент", result.error)

    def test_exit_with_too_many_arguments(self):
        result = self.shell.execute("exit 1 2")
        self.assertFalse(result.exit_requested)
        self.assertIn("слишком много", result.error)


if __name__ == "__main__":
    unittest.main()
