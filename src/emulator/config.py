"""Command-line configuration."""

import argparse


def build_parser():
    """Create command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="UNIX shell emulator",
    )
    parser.add_argument(
        "--vfs",
        help="Path to the physical VFS directory",
    )
    parser.add_argument(
        "--script",
        help="Path to the startup script",
    )
    return parser


def parse_arguments(arguments=None):
    """Parse command-line arguments."""
    parser = build_parser()
    return parser.parse_args(arguments)


def print_configuration(config):
    """Print application configuration for debugging."""
    vfs_path = config.vfs or "<not set>"
    script_path = config.script or "<not set>"

    print("Configuration:")
    print(f"VFS path: {vfs_path}")
    print(f"Startup script: {script_path}")
