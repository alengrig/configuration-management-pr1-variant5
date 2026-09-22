"""Interactive shell implementation."""

import getpass
import socket

DEFAULT_HEAD_LINES = 10
NO_ARGUMENTS = 0
ONE_ARGUMENT = 1
THREE_ARGUMENTS = 3
MIN_HEAD_LINES = 1


class Shell:
    """Simple command shell emulator."""

    def __init__(self, vfs=None):
        """Initialize shell state."""
        self.running = True
        self.vfs = vfs
        self.current_directory = "/"

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

        if command == "exit":
            self.running = False
            return True

        handlers = {
            "ls": self._command_ls,
            "cd": self._command_cd,
            "pwd": self._command_pwd,
            "cat": self._command_cat,
            "head": self._command_head,
        }
        handler = handlers.get(command)

        if handler is None:
            print(f"Error: unknown command: {command}")
            return False

        return handler(arguments)

    def _command_ls(self, arguments):
        """List VFS directory contents."""
        if self.vfs is None:
            print(f"ls: {arguments}")
            return True

        if len(arguments) > ONE_ARGUMENT:
            print("Error: ls: too many arguments")
            return False

        path = arguments[0] if arguments else "."
        target = self.vfs.resolve_path(self.current_directory, path)

        if self.vfs.is_file(target):
            print(target.rsplit("/", maxsplit=ONE_ARGUMENT)[-ONE_ARGUMENT])
            return True

        if not self.vfs.is_directory(target):
            print(f"Error: ls: no such path: {path}")
            return False

        for name in self.vfs.list_directory(target):
            print(name)

        return True

    def _command_cd(self, arguments):
        """Change current VFS directory."""
        if self.vfs is None:
            print(f"cd: {arguments}")
            return True

        if len(arguments) != ONE_ARGUMENT:
            print("Error: cd: expected one argument")
            return False

        path = arguments[0]
        target = self.vfs.resolve_path(self.current_directory, path)

        if not self.vfs.is_directory(target):
            print(f"Error: cd: no such directory: {path}")
            return False

        self.current_directory = target
        return True

    def _command_pwd(self, arguments):
        """Print current VFS directory."""
        if len(arguments) != NO_ARGUMENTS:
            print("Error: pwd: no arguments expected")
            return False

        print(self.current_directory)
        return True

    def _command_cat(self, arguments):
        """Print a text file from VFS."""
        if not self._check_file_arguments("cat", arguments):
            return False

        path = arguments[0]
        target = self.vfs.resolve_path(self.current_directory, path)

        if not self.vfs.is_file(target):
            print(f"Error: cat: no such file: {path}")
            return False

        return self._print_file(target)

    def _command_head(self, arguments):
        """Print the first lines of a VFS text file."""
        parsed = self._parse_head_arguments(arguments)

        if parsed is None:
            return False

        line_count, path = parsed
        target = self.vfs.resolve_path(self.current_directory, path)

        if not self.vfs.is_file(target):
            print(f"Error: head: no such file: {path}")
            return False

        return self._print_file(target, line_count)

    def _parse_head_arguments(self, arguments):
        """Parse supported head command arguments."""
        if len(arguments) == ONE_ARGUMENT:
            return DEFAULT_HEAD_LINES, arguments[0]

        valid_count = len(arguments) == THREE_ARGUMENTS
        if not valid_count or arguments[0] != "-n":
            print("Error: head: expected FILE or -n N FILE")
            return None

        try:
            line_count = int(arguments[1])
        except ValueError:
            print("Error: head: line count must be an integer")
            return None

        if line_count < MIN_HEAD_LINES:
            print("Error: head: line count must be positive")
            return None

        return line_count, arguments[2]

    def _check_file_arguments(self, command, arguments):
        """Validate common file command arguments."""
        if self.vfs is None:
            print(f"Error: {command}: VFS is not loaded")
            return False

        if len(arguments) != ONE_ARGUMENT:
            print(f"Error: {command}: expected one argument")
            return False

        return True

    def _print_file(self, path, line_count=None):
        """Decode and print a VFS text file."""
        try:
            text = self.vfs.files[path].decode("utf-8")
        except UnicodeDecodeError:
            print("Error: file is not valid UTF-8 text")
            return False

        if line_count is not None:
            lines = text.splitlines(keepends=True)
            text = "".join(lines[:line_count])

        print(text, end="")

        if not text.endswith("\n"):
            print()

        return True

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
