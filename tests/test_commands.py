"""Tests for stage 4 shell commands."""

import unittest
from contextlib import redirect_stdout
from io import StringIO

from emulator.shell import Shell
from emulator.vfs import VirtualFileSystem


class CommandTests(unittest.TestCase):
    """Test commands working with the in-memory VFS."""

    def setUp(self):
        """Create a small VFS for every test."""
        vfs = VirtualFileSystem()
        vfs.directories.update(
            {
                "/docs",
                "/docs/deep",
            }
        )
        vfs.files["/readme.txt"] = b"root\n"
        vfs.files["/docs/guide.txt"] = (
            b"line 1\nline 2\nline 3\n"
        )
        self.shell = Shell(vfs)

    def execute(self, command, arguments=None):
        """Execute a command and capture its output."""
        output = StringIO()

        with redirect_stdout(output):
            result = self.shell.execute(
                command,
                arguments or [],
            )

        return result, output.getvalue()

    def test_pwd_root(self):
        """Pwd should initially print root."""
        result, output = self.execute("pwd")

        self.assertTrue(result)
        self.assertEqual(output.strip(), "/")

    def test_ls_root(self):
        """Ls should list direct root children."""
        result, output = self.execute("ls")

        self.assertTrue(result)
        self.assertEqual(
            output.splitlines(),
            ["docs", "readme.txt"],
        )

    def test_cd_relative(self):
        """Cd should support relative directory paths."""
        result, _ = self.execute("cd", ["docs"])

        self.assertTrue(result)
        self.assertEqual(self.shell.current_directory, "/docs")

    def test_cd_parent(self):
        """Cd should support parent directory."""
        self.shell.current_directory = "/docs"
        result, _ = self.execute("cd", [".."])

        self.assertTrue(result)
        self.assertEqual(self.shell.current_directory, "/")

    def test_cd_absolute(self):
        """Cd should support absolute paths."""
        result, _ = self.execute("cd", ["/docs/deep"])

        self.assertTrue(result)
        self.assertEqual(
            self.shell.current_directory,
            "/docs/deep",
        )

    def test_cd_missing(self):
        """Cd should fail for a missing directory."""
        result, output = self.execute("cd", ["missing"])

        self.assertFalse(result)
        self.assertIn("no such directory", output)

    def test_cat(self):
        """Cat should print a file."""
        result, output = self.execute(
            "cat",
            ["/readme.txt"],
        )

        self.assertTrue(result)
        self.assertEqual(output, "root\n")

    def test_head_default(self):
        """Head should print a short file completely."""
        result, output = self.execute(
            "head",
            ["/docs/guide.txt"],
        )

        self.assertTrue(result)
        self.assertEqual(
            output,
            "line 1\nline 2\nline 3\n",
        )

    def test_head_line_count(self):
        """Head should support the -n option."""
        result, output = self.execute(
            "head",
            ["-n", "2", "/docs/guide.txt"],
        )

        self.assertTrue(result)
        self.assertEqual(output, "line 1\nline 2\n")

    def test_cat_missing(self):
        """Cat should report a missing file."""
        result, output = self.execute(
            "cat",
            ["missing.txt"],
        )

        self.assertFalse(result)
        self.assertIn("no such file", output)


if __name__ == "__main__":
    unittest.main()
