"""In-memory virtual file system."""

import posixpath
from pathlib import Path


class VFSError(Exception):
    """Error raised while loading the virtual file system."""


class VirtualFileSystem:
    """Store a directory tree completely in memory."""

    def __init__(self):
        """Initialize an empty virtual file system."""
        self.name = ""
        self.files = {}
        self.directories = {"/"}

    @classmethod
    def from_directory(cls, path):
        """Load a physical directory into memory."""
        root = Path(path)

        if not root.exists():
            raise VFSError("VFS directory does not exist")

        if not root.is_dir():
            raise VFSError("VFS path is not a directory")

        vfs = cls()
        vfs.name = root.name
        vfs._load_directory(root)
        return vfs

    def _load_directory(self, root):
        """Copy directory contents into memory."""
        try:
            for item in root.rglob("*"):
                self._load_item(root, item)
        except OSError as error:
            message = f"cannot read VFS directory: {error}"
            raise VFSError(message) from error

    def _load_item(self, root, item):
        """Copy one physical item into virtual storage."""
        relative = item.relative_to(root).as_posix()
        virtual_path = f"/{relative}"

        if item.is_dir():
            self.directories.add(virtual_path)
            return

        if item.is_file():
            self.files[virtual_path] = item.read_bytes()

    def resolve_path(self, current_directory, path):
        """Convert a shell path to an absolute VFS path."""
        if path.startswith("/"):
            candidate = path
        else:
            candidate = posixpath.join(current_directory, path)

        return posixpath.normpath(candidate)

    def is_directory(self, path):
        """Return whether path points to a directory."""
        return path in self.directories

    def is_file(self, path):
        """Return whether path points to a file."""
        return path in self.files

    def list_directory(self, path):
        """Return direct children of a directory."""
        names = set()

        for directory in self.directories:
            name = self._direct_child(path, directory)
            if name:
                names.add(name)

        for file_path in self.files:
            name = self._direct_child(path, file_path)
            if name:
                names.add(name)

        return sorted(names)

    def _direct_child(self, parent, candidate):
        """Return child name when candidate is directly below parent."""
        prefix = "/" if parent == "/" else f"{parent}/"

        if candidate == parent:
            return None

        if not candidate.startswith(prefix):
            return None

        remainder = candidate[len(prefix):]

        if not remainder or "/" in remainder:
            return None

        return remainder
