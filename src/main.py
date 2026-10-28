"""Entry point of the shell emulator."""
import sys

from gui import TerminalWindow
from identity import get_identity, window_title
from shell import Shell


def main():
    """Start the emulator window and return the process exit code."""
    user, host = get_identity()
    shell = Shell(user, host)
    window = TerminalWindow(shell, window_title(user, host))
    window.start()
    return 0


if __name__ == "__main__":
    sys.exit(main())
