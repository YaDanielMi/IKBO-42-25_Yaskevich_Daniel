"""Startup scripts: reading and replaying them as a dialog."""
from runner import run_line

SCRIPT_ENCODING = "utf-8-sig"


class ScriptError(Exception):
    """Raised when a startup script cannot be read."""


def read_script(path):
    """Return the lines of a startup script file (UTF-8)."""
    try:
        with open(path, encoding=SCRIPT_ENCODING) as stream:
            return stream.read().splitlines()
    except (OSError, UnicodeDecodeError) as error:
        message = f"не удалось прочитать скрипт {path}: {error}"
        raise ScriptError(message) from error


def run_script(shell, lines, view):
    """Replay script lines as if the user typed them.

    Both the input (with the prompt) and the output are shown in the
    view. Blank lines are skipped, comments are echoed and ignored by
    the parser. Errors do not stop the script. Returns the Result of
    the exit command if the script reached it, otherwise None.
    """
    for line in lines:
        if not line.strip():
            continue
        result = run_line(shell, line, view)
        if result.exit_requested:
            return result
    return None
