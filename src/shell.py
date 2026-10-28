"""Command line interpreter of the shell emulator."""
from cmdparser import ParseError, parse_line
from commands import COMMANDS
from result import Result

ROOT_DIR = "/"


class Shell:
    """State of the emulated shell and the command dispatcher."""

    def __init__(self, user, host):
        self.user = user
        self.host = host
        self.cwd = ROOT_DIR
        self.oldpwd = ROOT_DIR

    def prompt(self):
        """Return the prompt string, e.g. 'user@host:/$ '."""
        return f"{self.user}@{self.host}:{self.cwd}$ "

    def execute(self, line):
        """Parse and run one command line, return its Result."""
        try:
            tokens = parse_line(line)
        except ParseError as error:
            return Result(error=f"ошибка разбора: {error}")
        if not tokens:
            return Result()
        handler = COMMANDS.get(tokens[0])
        if handler is None:
            return Result(error=f"{tokens[0]}: команда не найдена")
        return handler(self, tokens[1:])
