"""Tests of the in-memory VFS."""
import os
import tempfile
import unittest

from vfs import (
    NOT_A_DIRECTORY, NOT_FOUND, Vfs, VfsError, load_directory,
)


def make_tree(base, files):
    """Create files (relative path -> text) under the base directory."""
    for relative, text in files.items():
        path = os.path.join(base, relative)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as stream:
            stream.write(text)


class VfsTestCase(unittest.TestCase):
    """Base class creating a small tree and loading it."""

    FILES = {
        "a.txt": "12345",
        "docs/b.txt": "xy",
        "docs/deep/c.txt": "",
        "empty/.keep": "",
    }

    def setUp(self):
        """Create the temporary tree and load it."""
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.path = folder.name
        make_tree(self.path, self.FILES)
        self.vfs = Vfs.from_directory(self.path)


class LoadTest(VfsTestCase):
    """Loading a directory into memory."""

    def test_count(self):
        self.assertEqual(self.vfs.count(), (3, 4))

    def test_file_content_and_size_are_loaded(self):
        _, node = self.vfs.resolve("/", "a.txt")
        self.assertEqual(node.data, b"12345")
        self.assertEqual(node.size, 5)

    def test_missing_directory(self):
        with self.assertRaises(VfsError):
            load_directory("/no/such/dir")

    def test_symlinks_are_skipped(self):
        os.symlink(self.path, os.path.join(self.path, "loop"))
        self.assertEqual(Vfs.from_directory(self.path).count(), (3, 4))

    def test_vfs_is_independent_of_disk(self):
        os.remove(os.path.join(self.path, "a.txt"))
        _, node = self.vfs.resolve("/", "a.txt")
        self.assertFalse(node.is_dir)

    def test_loading_does_not_modify_disk(self):
        before = sorted(os.walk(self.path))
        Vfs.from_directory(self.path)
        self.assertEqual(sorted(os.walk(self.path)), before)


class ResolveTest(VfsTestCase):
    """Path resolution."""

    def test_absolute_and_relative(self):
        self.assertEqual(self.vfs.resolve("/", "docs")[0], "/docs")
        self.assertEqual(self.vfs.resolve("/docs", "deep")[0], "/docs/deep")
        self.assertEqual(self.vfs.resolve("/docs", "/a.txt")[0], "/a.txt")

    def test_dot_and_dotdot(self):
        self.assertEqual(
            self.vfs.resolve("/docs/deep", "../../docs/./deep")[0],
            "/docs/deep",
        )

    def test_dotdot_above_root_stays_in_root(self):
        self.assertEqual(self.vfs.resolve("/", "../..")[0], "/")

    def test_empty_path_is_cwd(self):
        self.assertEqual(self.vfs.resolve("/docs", "")[0], "/docs")

    def test_trailing_slash(self):
        self.assertEqual(self.vfs.resolve("/", "docs/")[0], "/docs")

    def test_missing_component(self):
        with self.assertRaises(VfsError) as context:
            self.vfs.resolve("/", "docs/nope")
        self.assertEqual(str(context.exception), NOT_FOUND)

    def test_file_in_the_middle_of_a_path(self):
        with self.assertRaises(VfsError) as context:
            self.vfs.resolve("/", "a.txt/x")
        self.assertEqual(str(context.exception), NOT_A_DIRECTORY)

    def test_dotdot_after_a_file(self):
        with self.assertRaises(VfsError):
            self.vfs.resolve("/", "a.txt/..")


if __name__ == "__main__":
    unittest.main()
