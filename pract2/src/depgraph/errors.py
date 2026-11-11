"""Exceptions raised by the dependency graph tool."""


class DepGraphError(Exception):
    """Base class for all errors that are reported to the user."""


class ConfigError(DepGraphError):
    """A user supplied parameter has an invalid value."""
