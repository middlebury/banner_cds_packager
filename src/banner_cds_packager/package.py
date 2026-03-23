from pathlib import Path
import shutil
from zipfile import ZipFile

class Package:

    def copy_in_file(self, source: Path, destination: Path) -> None:
        """Copy a file's content into this package."""
        pass

    def create_file(self, content: str, destination: Path) -> None:
        """Add file content to a file path in this package."""
        pass

    def get_path(self) -> Path:
        """Answer the package path."""
        pass

    def delete(self) -> None:
        """Delete this package."""
        pass

    def validate_filename(self, destination: Path) -> bool:
        """Validate a filename and raise an exception if invalid"""
        allowed_extensions = ['.sql', '.pc', '.pks', '.pkb', '.jar', '.sh', '.shl', '.pl']
        if destination == Path("inst.txt"):
            return True
        elif destination.suffix in allowed_extensions:
            return True
        else:
            raise ValueError(f"File '{str(destination)}' is not 'inst.txt' or have one of the extensions allowed by Banner CDS ({', '.join(allowed_extensions)})")

class DirectoryPackage(Package):

    def __init__(self, output_directory: Path):
        self.output_directory = output_directory
        self.delete()

    def copy_in_file(self, source: Path, destination: Path) -> None:
        """Copy a file's content into this package."""
        self.validate_filename(destination)
        destination_path = self.output_directory / destination
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(source, destination_path)

    def create_file(self, content: str, destination: Path) -> None:
        """Add file content to a file path in this package."""
        self.validate_filename(destination)
        destination_path = self.output_directory / destination
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        destination_path.write_text(content)

    def get_path(self) -> Path:
        """Answer the package path."""
        return self.output_directory

    def delete(self) -> None:
        """Delete this package."""
        if self.output_directory.exists():
            shutil.rmtree(self.output_directory)

class ZipPackage(Package):

    def __init__(self, output_file: Path):
        if output_file.suffix != '.zip':
            raise ValueError("Output file must have a .zip extension.")
        self.output_file = output_file
        self.delete()
        self.zipfile = ZipFile(output_file, 'w')

    def copy_in_file(self, source: Path, destination: Path) -> None:
        """Copy a file's content into this package."""
        self.validate_filename(destination)
        self.zipfile.write(source, destination)

    def create_file(self, content: str, destination: Path) -> None:
        """Add file content to a file path in this package."""
        self.validate_filename(destination)
        self.zipfile.writestr(str(destination), content)

    def get_path(self) -> Path:
        """Answer the package path."""
        return self.output_file

    def delete(self) -> None:
        """Delete this package."""
        if self.output_file.exists():
            self.output_file.unlink()
