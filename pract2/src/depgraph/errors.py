"""Exceptions raised by the dependency graph tool."""


class DepGraphError(Exception):
    """Base class for all errors that are reported to the user."""


class ConfigError(DepGraphError):
    """A user supplied parameter has an invalid value."""


class RepositoryError(DepGraphError):
    """The repository cannot be read or has an invalid format."""


class PackageNotFoundError(RepositoryError):
    """The requested package does not exist in the repository."""


class RenderError(DepGraphError):
    """The image of the graph cannot be produced."""
