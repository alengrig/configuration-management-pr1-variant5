"""Tests for stage 4 shell commands."""

import unittest
from contextlib import redirect_stdout
from io import StringIO

from emulator.shell import Shell
from emulator.vfs import VirtualFileSystem


class CommandTests(unittest.TestCase):
    """Test commands working with the in-memory VFS."""

    def _create_shell(self):
        """Create a small VFS for a test."""
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
        return Shell(vfs)

    def _execute(self, shell, command, arguments=None):
        """Execute a command and capture its output."""
        output = StringIO()

        with redirect_stdout(output):
            result = shell.execute(
                command,
                arguments or [],
            )

        return result, output.getvalue()

    def test_pwd_root(self):
        """Pwd should initially print root."""
        shell = self._create_shell()
        result, output = self._execute(shell, "pwd")

        self.assertTrue(result)
        self.assertEqual(output.strip(), "/")

    def test_ls_root(self):
        """Ls should list direct root children."""
        shell = self._create_shell()
        result, output = self._execute(shell, "ls")

        self.assertTrue(result)
        self.assertEqual(
            output.splitlines(),
            ["docs", "readme.txt"],
        )

    def test_cd_relative(self):
        """Cd should support relative directory paths."""
        shell = self._create_shell()
        result, _ = self._execute(
            shell,
            "cd",
            ["docs"],
        )

        self.assertTrue(result)
        self.assertEqual(shell.current_directory, "/docs")

    def test_cd_parent(self):
        """Cd should support parent directory."""
        shell = self._create_shell()
        shell.current_directory = "/docs"

        result, _ = self._execute(
            shell,
            "cd",
            [".."],
        )

        self.assertTrue(result)
        self.assertEqual(shell.current_directory, "/")

    def test_cd_absolute(self):
        """Cd should support absolute paths."""
        shell = self._create_shell()
        result, _ = self._execute(
            shell,
            "cd",
            ["/docs/deep"],
        )

        self.assertTrue(result)
        self.assertEqual(
            shell.current_directory,
            "/docs/deep",
        )

    def test_cd_missing(self):
        """Cd should fail for a missing directory."""
        shell = self._create_shell()
        result, output = self._execute(
            shell,
            "cd",
            ["missing"],
        )

        self.assertFalse(result)
        self.assertIn("no such directory", output)

    def test_cat(self):
        """Cat should print a file."""
        shell = self._create_shell()
        result, output = self._execute(
            shell,
            "cat",
            ["/readme.txt"],
        )

        self.assertTrue(result)
        self.assertEqual(output, "root\n")

    def test_head_default(self):
        """Head should print a short file completely."""
        shell = self._create_shell()
        result, output = self._execute(
            shell,
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
        shell = self._create_shell()
        result, output = self._execute(
            shell,
            "head",
            ["-n", "2", "/docs/guide.txt"],
        )

        self.assertTrue(result)
        self.assertEqual(output, "line 1\nline 2\n")

    def test_cat_missing(self):
        """Cat should report a missing file."""
        shell = self._create_shell()
        result, output = self._execute(
            shell,
            "cat",
            ["missing.txt"],
        )

        self.assertFalse(result)
        self.assertIn("no such file", output)


if __name__ == "__main__":
    unittest.main()
