"""In-memory virtual file system."""

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
