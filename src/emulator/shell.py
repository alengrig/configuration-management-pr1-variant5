"""Interactive shell implementation."""

import getpass
import socket


class Shell:
    """Simple command shell emulator."""

    def __init__(self):
        """Initialize shell state."""
        self.running = True

    def build_prompt(self):
        """Build prompt from real operating system data."""
        username = getpass.getuser()
        hostname = socket.gethostname()
        return f"{username}@{hostname}:~$ "

    def parse_line(self, line):
        """Split input into command and arguments."""
        parts = line.split()

        if not parts:
            return "", []

        command = parts[0]
        arguments = parts[1:]
        return command, arguments

    def execute(self, command, arguments):
        """Execute one shell command."""
        if command == "":
            return

        if command == "ls":
            print(f"ls: {arguments}")
            return

        if command == "cd":
            print(f"cd: {arguments}")
            return

        if command == "exit":
            self.running = False
            return

        print(f"Error: unknown command: {command}")

    def run(self):
        """Run interactive read-eval-print loop."""
        while self.running:
            try:
                line = input(self.build_prompt())
            except EOFError:
                break

            command, arguments = self.parse_line(line)
            self.execute(command, arguments)

