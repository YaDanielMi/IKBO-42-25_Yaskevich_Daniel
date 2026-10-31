"""Command line parameters of the emulator and their validation."""
import argparse
import os
from dataclasses import dataclass
from typing import Optional

NOT_SET = "<не задан>"


class ConfigError(Exception):
    """Raised when a parameter value is not usable."""


@dataclass
class Config:
    """Parameters given on the command line."""

    vfs_path: Optional[str] = None
    script_path: Optional[str] = None
    headless: bool = False


def build_parser():
    """Create the argparse parser of the emulator."""
    parser = argparse.ArgumentParser(
        prog="emulator",
        description="Эмулятор командной оболочки UNIX-подобной ОС.",
    )
    parser.add_argument(
        "--vfs", metavar="PATH", dest="vfs_path",
        help="путь к каталогу на диске, из которого строится VFS",
    )
    parser.add_argument(
        "--script", metavar="PATH", dest="script_path",
        help="путь к стартовому скрипту с командами эмулятора",
    )
    parser.add_argument(
        "--headless", action="store_true",
        help="работать в консоли без графического окна",
    )
    return parser


def parse_args(argv=None):
    """Parse command line arguments into a Config."""
    namespace = build_parser().parse_args(argv)
    return Config(**vars(namespace))


def _describe_path(value):
    """Show a path as given and in its absolute form."""
    if value is None:
        return NOT_SET
    return f"{value} (абсолютный путь: {os.path.abspath(value)})"


def debug_lines(config):
    """Return debug lines listing every parameter of the run."""
    return [
        "[debug] параметры запуска эмулятора:",
        f"[debug]   --vfs      = {_describe_path(config.vfs_path)}",
        f"[debug]   --script   = {_describe_path(config.script_path)}",
        f"[debug]   --headless = {config.headless}",
    ]


def validate(config):
    """Check that the given paths exist, raise ConfigError otherwise."""
    if config.vfs_path is not None and not os.path.isdir(config.vfs_path):
        raise ConfigError(f"каталог VFS не найден: {config.vfs_path}")
    script = config.script_path
    if script is not None and not os.path.isfile(script):
        raise ConfigError(f"стартовый скрипт не найден: {script}")
