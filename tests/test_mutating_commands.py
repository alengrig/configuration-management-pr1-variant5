"""Tests for stage 5 commands that modify VFS state."""

import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from emulator.shell import Shell
from emulator.vfs import VirtualFileSystem


class MutatingCommandTests(unittest.TestCase):
    """Test rm and cp commands."""

    def _create_shell(self):
        """Create an in-memory VFS for a test."""
        vfs = VirtualFileSystem()
        vfs.directories.add("/docs")
        vfs.files["/readme.txt"] = b"root\n"
        return Shell(vfs)

    def _execute(self, shell, command, arguments):
        """Execute a command and capture its output."""
        output = StringIO()

        with redirect_stdout(output):
            result = shell.execute(
                command,
                arguments,
            )

        return result, output.getvalue()

    def test_rm_file(self):
        """Rm should remove a file from memory."""
        shell = self._create_shell()
        result, _ = self._execute(
            shell,
            "rm",
            ["readme.txt"],
        )

        self.assertTrue(result)
        self.assertNotIn(
            "/readme.txt",
            shell.vfs.files,
        )

    def test_rm_missing_file(self):
        """Rm should report a missing file."""
        shell = self._create_shell()
        result, output = self._execute(
            shell,
            "rm",
            ["missing.txt"],
        )

        self.assertFalse(result)
        self.assertIn("no such file", output)

    def test_cp_file(self):
        """Cp should create an in-memory copy."""
        shell = self._create_shell()
        result, _ = self._execute(
            shell,
            "cp",
            ["readme.txt", "copy.txt"],
        )

        self.assertTrue(result)
        self.assertEqual(
            shell.vfs.files["/copy.txt"],
            b"root\n",
        )

    def test_cp_to_directory(self):
        """Cp should copy a file into a directory."""
        shell = self._create_shell()
        result, _ = self._execute(
            shell,
            "cp",
            ["readme.txt", "docs"],
        )

        self.assertTrue(result)
        self.assertEqual(
            shell.vfs.files["/docs/readme.txt"],
            b"root\n",
        )

    def test_cp_missing_source(self):
        """Cp should report a missing source."""
        shell = self._create_shell()
        result, output = self._execute(
            shell,
            "cp",
            ["missing.txt", "copy.txt"],
        )

        self.assertFalse(result)
        self.assertIn("no such file", output)

    def test_cp_missing_parent(self):
        """Cp should reject a missing destination directory."""
        shell = self._create_shell()
        result, output = self._execute(
            shell,
            "cp",
            ["readme.txt", "missing/copy.txt"],
        )

        self.assertFalse(result)
        self.assertIn("destination directory", output)

    def test_rm_does_not_delete_physical_file(self):
        """Rm must not delete the physical VFS source."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            file_path = root / "file.txt"
            file_path.write_text("physical", encoding="utf-8")
            vfs = VirtualFileSystem.from_directory(root)
            shell = Shell(vfs)

            shell.execute("rm", ["file.txt"])

            self.assertTrue(file_path.exists())

    def test_cp_does_not_create_physical_file(self):
        """Cp must not create files in the physical VFS."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "file.txt"
            source.write_text("physical", encoding="utf-8")
            vfs = VirtualFileSystem.from_directory(root)
            shell = Shell(vfs)

            shell.execute(
                "cp",
                ["file.txt", "copy.txt"],
            )

            self.assertFalse((root / "copy.txt").exists())


if __name__ == "__main__":
    unittest.main()
