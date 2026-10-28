"""Result of executing one command line."""
from dataclasses import dataclass


@dataclass
class Result:
    """Text written to stdout/stderr and the exit request, if any."""

    output: str = ""
    error: str = ""
    exit_requested: bool = False
    exit_code: int = 0
