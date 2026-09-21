"""Tests for command-line configuration."""

import unittest
from contextlib import redirect_stdout
from io import StringIO

from emulator.config import parse_arguments
from emulator.config import print_configuration


class ConfigurationTests(unittest.TestCase):
    """Test command-line configuration."""

    def test_default_configuration(self):
        """Arguments should be optional."""
        config = parse_arguments([])

        self.assertIsNone(config.vfs)
        self.assertIsNone(config.script)

    def test_vfs_argument(self):
        """VFS path should be read from command line."""
        config = parse_arguments(
            ["--vfs", "examples/vfs/basic"],
        )

        self.assertEqual(config.vfs, "examples/vfs/basic")

    def test_script_argument(self):
        """Startup script path should be read."""
        config = parse_arguments(
            ["--script", "startup.txt"],
        )

        self.assertEqual(config.script, "startup.txt")

    def test_all_arguments(self):
        """Both supported arguments should be parsed."""
        config = parse_arguments(
            [
                "--vfs",
                "vfs",
                "--script",
                "startup.txt",
            ],
        )

        self.assertEqual(config.vfs, "vfs")
        self.assertEqual(config.script, "startup.txt")

    def test_debug_output(self):
        """Configuration should be printed for debugging."""
        config = parse_arguments(
            ["--vfs", "vfs"],
        )
        output = StringIO()

        with redirect_stdout(output):
            print_configuration(config)

        text = output.getvalue()
        self.assertIn("VFS path: vfs", text)
        self.assertIn("Startup script: <not set>", text)


if __name__ == "__main__":
    unittest.main()
