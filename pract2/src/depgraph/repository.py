"""Selection of the repository implementation."""

from depgraph.file_repository import FileRepository
from depgraph.npm_repository import NpmRepository


def open_repository(config):
    """Open the test repository file or the npm registry."""
    if config.test_mode:
        return FileRepository.from_file(config.repo)
    return NpmRepository(config.repo)
