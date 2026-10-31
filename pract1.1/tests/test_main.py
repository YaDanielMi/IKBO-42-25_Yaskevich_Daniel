"""End-to-end tests of main()."""
import contextlib
import io
import os
import tempfile
import unittest
from unittest import mock

from main import EXIT_FAILURE, main


class MainTest(unittest.TestCase):
    """Running main() in headless mode."""

    def run_main(self, argv, stdin_text=""):
        """Return (exit code, stdout, stderr) of main(argv)."""
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out):
            with contextlib.redirect_stderr(err):
                with mock.patch("sys.stdin", io.StringIO(stdin_text)):
                    code = main(argv)
        return code, out.getvalue(), err.getvalue()

    def test_debug_output_lists_parameters(self):
        _, out, _ = self.run_main(["--headless"])
        self.assertIn("[debug]   --headless = True", out)

    def test_script_exit_code_is_returned(self):
        with tempfile.TemporaryDirectory() as folder:
            script = os.path.join(folder, "s.emu")
            with open(script, "w", encoding="utf-8") as stream:
                stream.write("# demo\nls\nexit 9\n")
            code, out, _ = self.run_main(["--headless", "--script", script])
        self.assertEqual(code, 9)
        self.assertIn("ls: заглушка", out)

    def test_vfs_is_loaded_and_used(self):
        with tempfile.TemporaryDirectory() as folder:
            os.makedirs(os.path.join(folder, "sub"))
            code, out, _ = self.run_main(
                ["--headless", "--vfs", folder], "cd sub\nexit 4\n"
            )
        self.assertEqual(code, 4)
        self.assertIn("VFS загружена в память: каталогов 1", out)
        self.assertIn(":/sub$ ", out)

    def test_bad_vfs_is_reported(self):
        code, out, err = self.run_main(["--headless", "--vfs", "/no/dir"])
        self.assertEqual(code, EXIT_FAILURE)
        self.assertIn("[debug]", out)
        self.assertIn("Ошибка", err)

    def test_bad_script_is_reported(self):
        argv = ["--headless", "--script", "/no/script"]
        code, _, err = self.run_main(argv)
        self.assertEqual(code, EXIT_FAILURE)
        self.assertIn("Ошибка", err)


if __name__ == "__main__":
    unittest.main()
