import typer

from .create_banner_cds_package import create_banner_cds_package

app = typer.Typer()
app.command(help="Package changes to a Banner repository for deployment via Banner CDS. Must be run from within a git repository or git working directory.")(create_banner_cds_package)

if __name__ == "__main__":
    app()
