"""Console front end used by the --headless mode."""
import sys

from runner import show_result
from script import run_script

EOF_ECHO = "exit"


class ConsoleView:
    """Text view writing to standard streams."""

    def __init__(self, in_stream=None, out_stream=None, err_stream=None):
        self.in_stream = in_stream or sys.stdin
        self.out_stream = out_stream or sys.stdout
        self.err_stream = err_stream or sys.stderr

    def _write(self, stream, text):
        """Write text to a stream and flush it to keep the ordering."""
        stream.write(text)
        stream.flush()

    def echo(self, prompt, line):
        """Show a prompt followed by a command line."""
        self._write(self.out_stream, f"{prompt}{line}\n")

    def out(self, text):
        """Show standard output of a command."""
        self._write(self.out_stream, text + "\n")

    def err(self, text):
        """Show standard error of a command."""
        self._write(self.err_stream, text + "\n")

    def read(self, prompt):
        """Print the prompt and read a line, None means end of input.

        When the input is not a terminal the line is echoed so that the
        output looks like a real dialog.
        """
        self._write(self.out_stream, prompt)
        line = self.in_stream.readline()
        if not line:
            self.out(EOF_ECHO)
            return None
        line = line.rstrip("\n")
        if not self.in_stream.isatty():
            self.out(line)
        return line


def interact(shell, view):
    """Read and run commands until exit or end of input."""
    while True:
        line = view.read(shell.prompt())
        if line is None:
            return 0
        result = shell.execute(line)
        show_result(result, view)
        if result.exit_requested:
            return result.exit_code


def run_headless(shell, view, script_lines):
    """Replay the startup script, then continue interactively.

    Returns the process exit code.
    """
    result = run_script(shell, script_lines, view)
    if result is not None:
        return result.exit_code
    return interact(shell, view)
