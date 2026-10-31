"""Tests of ls and cd working on a VFS."""
import unittest

from shell import Shell
from test_vfs import VfsTestCase
from vfs import Node


class CommandsTestCase(VfsTestCase):
    """Base class: a shell attached to the test VFS."""

    def setUp(self):
        """Attach a shell to the VFS."""
        super().setUp()
        self.shell = Shell("u", "h", self.vfs)

    def lines(self, command):
        """Run a command and return its stdout lines."""
        return self.shell.execute(command).output.splitlines()


class LsTest(CommandsTestCase):
    """The ls command."""

    def test_current_directory_hides_dotfiles(self):
        self.assertEqual(self.lines("ls"), ["a.txt", "docs", "empty"])

    def test_empty_directory_prints_nothing(self):
        self.assertEqual(self.shell.execute("ls empty").output, "")

    def test_all_flag(self):
        self.assertEqual(self.lines("ls -a empty"), [".", "..", ".keep"])

    def test_long_flag_aligns_sizes(self):
        self.assertEqual(
            self.lines("ls -l"),
            ["- 5 a.txt", "d 0 docs", "d 0 empty"],
        )

    def test_combined_flags(self):
        self.assertEqual(self.lines("ls -la empty")[0], "d 0 .")

    def test_path_argument(self):
        self.assertEqual(self.lines("ls docs"), ["b.txt", "deep"])

    def test_file_argument_prints_the_given_path(self):
        self.assertEqual(self.lines("ls docs/b.txt"), ["docs/b.txt"])

    def test_several_directories_have_headers(self):
        self.assertEqual(
            self.shell.execute("ls docs empty").output,
            "docs:\nb.txt\ndeep\n\nempty:",
        )

    def test_files_come_first_in_one_block(self):
        output = self.shell.execute("ls docs a.txt docs/b.txt").output
        self.assertTrue(output.startswith("a.txt\ndocs/b.txt\n\ndocs:"))

    def test_quoted_name_with_spaces(self):
        docs = self.vfs.root.children["docs"]
        docs.children["my file"] = Node("my file", False)
        self.assertEqual(self.lines('ls "docs/my file"'), ["docs/my file"])

    def test_missing_path(self):
        result = self.shell.execute("ls nope")
        self.assertIn("'nope'", result.error)
        self.assertIn("Нет такого файла", result.error)

    def test_error_does_not_hide_other_output(self):
        result = self.shell.execute("ls nope docs")
        self.assertIn("b.txt", result.output)
        self.assertIn("nope", result.error)

    def test_file_in_the_middle_of_a_path(self):
        self.assertIn("Не каталог", self.shell.execute("ls a.txt/x").error)

    def test_unknown_short_option(self):
        self.assertIn("-- 'z'", self.shell.execute("ls -z").error)

    def test_unknown_long_option(self):
        self.assertIn("--zz", self.shell.execute("ls --zz").error)

    def test_double_dash_ends_options(self):
        self.assertIn("'-l'", self.shell.execute("ls -- -l").error)

    def test_relative_to_cwd(self):
        self.shell.execute("cd docs")
        self.assertEqual(self.lines("ls deep"), ["c.txt"])


class CdTest(CommandsTestCase):
    """The cd command."""

    def test_relative_and_prompt(self):
        self.shell.execute("cd docs/deep")
        self.assertEqual(self.shell.cwd, "/docs/deep")
        self.assertEqual(self.shell.prompt(), "u@h:/docs/deep$ ")

    def test_absolute(self):
        self.shell.execute("cd /docs/deep")
        self.shell.execute("cd /empty")
        self.assertEqual(self.shell.cwd, "/empty")

    def test_without_arguments_goes_to_root(self):
        self.shell.execute("cd docs")
        self.shell.execute("cd")
        self.assertEqual(self.shell.cwd, "/")

    def test_parent_and_above_root(self):
        self.shell.execute("cd docs/deep")
        self.shell.execute("cd ../../../..")
        self.assertEqual(self.shell.cwd, "/")

    def test_dash_returns_and_prints(self):
        self.shell.execute("cd docs")
        self.shell.execute("cd deep")
        result = self.shell.execute("cd -")
        self.assertEqual(result.output, "/docs")
        self.assertEqual(self.shell.cwd, "/docs")

    def test_dash_without_history(self):
        result = self.shell.execute("cd -")
        self.assertIn("OLDPWD", result.error)
        self.assertEqual(self.shell.cwd, "/")

    def test_missing_directory_keeps_cwd(self):
        result = self.shell.execute("cd nope")
        self.assertIn("cd: nope:", result.error)
        self.assertEqual(self.shell.cwd, "/")

    def test_file_is_not_a_directory(self):
        result = self.shell.execute("cd a.txt")
        self.assertIn("Не каталог", result.error)
        self.assertEqual(self.shell.cwd, "/")

    def test_too_many_arguments(self):
        result = self.shell.execute("cd docs empty")
        self.assertIn("слишком много", result.error)

    def test_quoted_argument(self):
        self.vfs.root.children["a b"] = Node("a b", True)
        self.shell.execute('cd "a b"')
        self.assertEqual(self.shell.cwd, "/a b")


class StubTest(unittest.TestCase):
    """Without a VFS the commands stay stubs."""

    def test_stubs_without_vfs(self):
        shell = Shell("u", "h")
        self.assertIn("заглушка", shell.execute("ls x").output)
        self.assertIn("заглушка", shell.execute("cd x").output)


if __name__ == "__main__":
    unittest.main()
