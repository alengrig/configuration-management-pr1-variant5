"""Application entry point."""

from emulator.config import parse_arguments
from emulator.config import print_configuration
from emulator.shell import Shell
from emulator.vfs import VFSError
from emulator.vfs import VirtualFileSystem


def load_vfs(path):
    """Load VFS when its path is specified."""
    if path is None:
        return None

    try:
        vfs = VirtualFileSystem.from_directory(path)
    except VFSError as error:
        print(f"Error: {error}")
        return None

    print(f"Loaded VFS: {vfs.name}")
    return vfs


def main():
    """Start the command shell emulator."""
    config = parse_arguments()
    print_configuration(config)

    vfs = load_vfs(config.vfs)

    if config.vfs and vfs is None:
        return 1

    shell = Shell(vfs)

    if config.script:
        if not shell.run_script(config.script):
            return 1

    if shell.running:
        shell.run()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
