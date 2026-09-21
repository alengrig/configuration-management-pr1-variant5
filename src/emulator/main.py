"""Application entry point."""

from emulator.shell import Shell


def main():
    """Start the command shell emulator."""
    shell = Shell()
    shell.run()


if __name__ == "__main__":
    main()
