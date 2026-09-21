"""Tests for the in-memory virtual file system."""

import tempfile
import unittest
from pathlib import Path

from emulator.vfs import VFSError
from emulator.vfs import VirtualFileSystem


class VirtualFileSystemTests(unittest.TestCase):
    """Test loading VFS data into memory."""

    def test_load_file(self):
        """A physical file should be copied into memory."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            file_path = root / "hello.txt"
            file_path.write_text("hello", encoding="utf-8")

            vfs = VirtualFileSystem.from_directory(root)

        self.assertEqual(vfs.files["/hello.txt"], b"hello")

    def test_load_nested_directory(self):
        """Nested directories should be represented."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            nested = root / "one" / "two" / "three"
            nested.mkdir(parents=True)

            vfs = VirtualFileSystem.from_directory(root)

        self.assertIn("/one", vfs.directories)
        self.assertIn("/one/two", vfs.directories)
        self.assertIn("/one/two/three", vfs.directories)

    def test_missing_directory(self):
        """Missing VFS directory should raise an error."""
        with self.assertRaises(VFSError):
            VirtualFileSystem.from_directory(
                "directory-that-does-not-exist",
            )

    def test_file_is_not_directory(self):
        """A file cannot be used as VFS root."""
        with tempfile.TemporaryDirectory() as directory:
            file_path = Path(directory) / "file.txt"
            file_path.write_text("data", encoding="utf-8")

            with self.assertRaises(VFSError):
                VirtualFileSystem.from_directory(file_path)

    def test_changes_stay_in_memory(self):
        """Changing VFS data must not change physical files."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            file_path = root / "hello.txt"
            file_path.write_text("physical", encoding="utf-8")

            vfs = VirtualFileSystem.from_directory(root)
            vfs.files["/hello.txt"] = b"virtual"

            physical = file_path.read_text(encoding="utf-8")

        self.assertEqual(physical, "physical")
        self.assertEqual(vfs.files["/hello.txt"], b"virtual")


if __name__ == "__main__":
    unittest.main()
