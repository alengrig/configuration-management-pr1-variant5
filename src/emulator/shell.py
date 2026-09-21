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

        return parts[0], parts[1:]

    def execute(self, command, arguments):
        """Execute one shell command."""
        if command == "":
            return True

        if command == "ls":
            print(f"ls: {arguments}")
            return True

        if command == "cd":
            print(f"cd: {arguments}")
            return True

        if command == "exit":
            self.running = False
            return True

        print(f"Error: unknown command: {command}")
        return False

    def run_script(self, path):
        """Execute commands from a startup script."""
        try:
            with open(path, encoding="utf-8") as script:
                return self._run_script_lines(script)
        except OSError as error:
            print(f"Error: cannot read startup script: {error}")
            return False

    def _run_script_lines(self, lines):
        """Execute startup script lines until an error occurs."""
        for number, raw_line in enumerate(lines, start=1):
            line = raw_line.strip()

            if not line:
                continue

            print(f"{self.build_prompt()}{line}")
            command, arguments = self.parse_line(line)

            if not self.execute(command, arguments):
                print(f"Error: startup script stopped at line {number}")
                return False

            if not self.running:
                break

        return True

    def run(self):
        """Run interactive read-eval-print loop."""
        while self.running:
            try:
                line = input(self.build_prompt())
            except EOFError:
                break

            command, arguments = self.parse_line(line)
            self.execute(command, arguments)
