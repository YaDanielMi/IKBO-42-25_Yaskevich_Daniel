"""Entry point of the shell emulator."""
import sys

from config import ConfigError, debug_lines, parse_args, validate
from console import ConsoleView, run_headless
from identity import get_identity, window_title
from script import ScriptError, read_script
from shell import Shell
from vfs import Vfs, VfsError

EXIT_OK = 0
EXIT_FAILURE = 1


def run_gui(shell, notices, script_lines):
    """Open the emulator window, return the process exit code."""
    try:
        from gui import TclError, TerminalWindow
    except ImportError:
        print("Ошибка: tkinter не установлен, "
              "используйте --headless", file=sys.stderr)
        return EXIT_FAILURE
    title = window_title(shell.user, shell.host)
    try:
        window = TerminalWindow(shell, title)
    except TclError as error:
        print(f"Ошибка: графика недоступна ({error}), "
              "используйте --headless", file=sys.stderr)
        return EXIT_FAILURE
    window.start(notices, script_lines)
    return EXIT_OK


def load_inputs(config):
    """Validate the parameters and load the VFS and the script.

    Returns (vfs or None, script lines, extra debug lines).
    """
    validate(config)
    vfs, lines, notices = None, [], []
    if config.vfs_path is not None:
        vfs = Vfs.from_directory(config.vfs_path)
        dirs, files = vfs.count()
        notices.append(
            f"[debug] VFS загружена в память: каталогов {dirs}, "
            f"файлов {files}"
        )
    if config.script_path is not None:
        lines = read_script(config.script_path)
    return vfs, lines, notices


def main(argv=None):
    """Run the emulator and return the process exit code."""
    config = parse_args(argv)
    notices = debug_lines(config)
    print("\n".join(notices), flush=True)
    try:
        vfs, script_lines, extra = load_inputs(config)
    except (ConfigError, ScriptError, VfsError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return EXIT_FAILURE
    if extra:
        print("\n".join(extra), flush=True)
    shell = Shell(*get_identity(), vfs)
    if config.headless:
        return run_headless(shell, ConsoleView(), script_lines)
    return run_gui(shell, notices + extra, script_lines)


if __name__ == "__main__":
    sys.exit(main())
