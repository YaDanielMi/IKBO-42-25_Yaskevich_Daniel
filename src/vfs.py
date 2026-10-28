"""In-memory virtual file system built from a directory on disk."""
import os
from dataclasses import dataclass, field

ROOT_PATH = "/"
SEPARATOR = "/"
CURRENT = "."
PARENT = ".."
NOT_FOUND = "Нет такого файла или каталога"
NOT_A_DIRECTORY = "Не каталог"


class VfsError(Exception):
    """Raised for failed VFS operations; the text is the reason."""


@dataclass
class Node:
    """A file (with its content) or a directory (with children)."""

    name: str
    is_dir: bool
    data: bytes = b""
    children: dict = field(default_factory=dict)

    @property
    def size(self):
        """Size of a file in bytes (zero for directories)."""
        return len(self.data)


def _read_file(path):
    """Read a whole file into memory."""
    with open(path, "rb") as stream:
        return stream.read()


def _fill(node, path):
    """Recursively copy the directory `path` into the node.

    Symbolic links and special files are skipped.
    """
    try:
        with os.scandir(path) as iterator:
            entries = list(iterator)
    except OSError as error:
        raise VfsError(f"не удалось прочитать {path}: {error}") from error
    for entry in entries:
        if entry.is_symlink():
            continue
        if entry.is_dir(follow_symlinks=False):
            child = Node(entry.name, True)
            _fill(child, entry.path)
        elif entry.is_file(follow_symlinks=False):
            child = Node(entry.name, False, _read_file(entry.path))
        else:
            continue
        node.children[entry.name] = child


def load_directory(path):
    """Read the directory tree from disk and return the root Node."""
    if not os.path.isdir(path):
        raise VfsError(f"каталог VFS не найден: {path}")
    root = Node("", True)
    _fill(root, path)
    return root


class Vfs:
    """Read-only file system living entirely in memory."""

    def __init__(self, root):
        self.root = root

    @classmethod
    def from_directory(cls, path):
        """Build a VFS from a directory on the real disk."""
        return cls(load_directory(path))

    def count(self):
        """Return (directories, files), the root is not counted."""
        dirs = files = 0
        stack = list(self.root.children.values())
        while stack:
            node = stack.pop()
            if node.is_dir:
                dirs += 1
                stack.extend(node.children.values())
            else:
                files += 1
        return dirs, files

    def _stack(self, cwd):
        """Return the chain of nodes from the root to `cwd`."""
        stack = [self.root]
        for part in cwd.split(SEPARATOR):
            if part:
                stack.append(stack[-1].children[part])
        return stack

    @staticmethod
    def _step(stack, part):
        """Move one path component forward or up in the node chain."""
        if part in ("", CURRENT):
            return
        if not stack[-1].is_dir:
            raise VfsError(NOT_A_DIRECTORY)
        if part == PARENT:
            if stack[1:]:
                stack.pop()
            return
        child = stack[-1].children.get(part)
        if child is None:
            raise VfsError(NOT_FOUND)
        stack.append(child)

    def resolve(self, cwd, path):
        """Find `path` (absolute or relative to `cwd`).

        Returns (absolute path, node). Raises VfsError if some
        component is missing or is a file in the middle of the path.
        """
        if path.startswith(SEPARATOR):
            stack = [self.root]
        else:
            stack = self._stack(cwd)
        for part in path.split(SEPARATOR):
            self._step(stack, part)
        names = [node.name for node in stack[1:]]
        return SEPARATOR + SEPARATOR.join(names), stack[-1]
