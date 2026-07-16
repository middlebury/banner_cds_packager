import typer

from .create_banner_cds_package import create
from .upload_banner_cds_package import upload

app = typer.Typer()
app.command(help="Package changes to a Banner repository for deployment via Banner CDS. Must be run from within a git repository or git working directory.")(create)
app.command(help="Upload a package to Banner CDS.")(upload)

if __name__ == "__main__":
    app()
