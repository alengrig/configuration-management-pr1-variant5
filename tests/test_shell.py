"""Tests for the stage 1 command shell."""

import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch

from emulator.shell import Shell


class ShellTests(unittest.TestCase):
    """Test basic shell behavior."""

    def setUp(self):
        """Create a fresh shell before every test."""
        self.shell = Shell()

    def test_parse_empty_line(self):
        """Empty input should produce no command."""
        command, arguments = self.shell.parse_line("")

        self.assertEqual(command, "")
        self.assertEqual(arguments, [])

    def test_parse_command(self):
        """A command without arguments should be parsed."""
        command, arguments = self.shell.parse_line("ls")

        self.assertEqual(command, "ls")
        self.assertEqual(arguments, [])

    def test_parse_command_with_arguments(self):
        """Arguments should be separated by spaces."""
        command, arguments = self.shell.parse_line(
            "ls docs file.txt"
        )

        self.assertEqual(command, "ls")
        self.assertEqual(arguments, ["docs", "file.txt"])

    def test_prompt_uses_os_data(self):
        """Prompt should contain username and hostname."""
        with patch(
            "emulator.shell.getpass.getuser",
            return_value="user",
        ):
            with patch(
                "emulator.shell.socket.gethostname",
                return_value="host",
            ):
                prompt = self.shell.build_prompt()

        self.assertEqual(prompt, "user@host:~$ ")

    def test_ls_stub(self):
        """The ls stub should print its arguments."""
        output = StringIO()

        with redirect_stdout(output):
            self.shell.execute("ls", ["docs"])

        self.assertEqual(output.getvalue().strip(), "ls: ['docs']")

    def test_cd_stub(self):
        """The cd stub should print its arguments."""
        output = StringIO()

        with redirect_stdout(output):
            self.shell.execute("cd", ["docs"])

        self.assertEqual(output.getvalue().strip(), "cd: ['docs']")

    def test_unknown_command(self):
        """Unknown commands should produce an error."""
        output = StringIO()

        with redirect_stdout(output):
            self.shell.execute("hello", [])

        expected = "Error: unknown command: hello"
        self.assertEqual(output.getvalue().strip(), expected)

    def test_exit_stops_shell(self):
        """Exit should change the running state."""
        self.shell.execute("exit", [])

        self.assertFalse(self.shell.running)


if __name__ == "__main__":
    unittest.main()
