from pathlib import Path
import shutil

class Package:

    def copy_in_file(self, source: Path, destination: Path) -> None:
        """Copy a file's content into this package."""
        pass

    def add_file(self, content: str, destination: Path) -> None:
        """Add file content to a file path in this package."""
        pass

    def save(self) -> Path:
        """Write any remaining output and return the resulting path."""
        pass

    def delete(self) -> None:
        """Delete this package."""
        pass

class DirectoryPackage(Package):

    def __init__(self, output_directory: Path):
        self.output_directory = output_directory
        self.delete()

    def copy_in_file(self, source: Path, destination: Path) -> None:
        """Copy a file's content into this package."""
        destination_path = self.output_directory / destination
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(source, destination_path)

    def add_file(self, content: str, destination: Path) -> None:
        """Add file content to a file path in this package."""
        destination_path = self.output_directory / destination
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        destination_path.write_text(content)

    def save(self) -> Path:
        """Write any remaining output and return the resulting path."""
        return self.output_directory

    def delete(self) -> None:
        """Delete this package."""
        if self.output_directory.exists():
            shutil.rmtree(self.output_directory)
