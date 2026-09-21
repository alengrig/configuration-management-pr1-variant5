"""Application entry point."""

from emulator.config import parse_arguments
from emulator.config import print_configuration
from emulator.shell import Shell


def main():
    """Start the command shell emulator."""
    config = parse_arguments()
    print_configuration(config)

    shell = Shell()

    if config.script:
        if not shell.run_script(config.script):
            return 1

    if shell.running:
        shell.run()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
